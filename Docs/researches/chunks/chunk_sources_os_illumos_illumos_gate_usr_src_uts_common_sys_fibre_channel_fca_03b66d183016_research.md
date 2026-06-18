# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h lines 6653-9970

## Scope

This chunk is the ordered interval `6653-9970` of `fw_lpe12000.h`, covering firmware-image offsets `0x0CF18` through `0x136C0` inclusive. It is entirely inside the `static uint8_t emlxs_lpe12000_image[]` initializer, so the chunk contributes about `26,544` bytes of the embedded LPe12000 firmware image rather than normal C control flow.

The parent header identifies the payload as `LPe12000-S: v2.01a4 (ud201a4.all)` and exposes firmware metadata through macros such as `emlxs_lpe12000_kern`, `emlxs_lpe12000_stub`, `emlxs_lpe12000_sli2`, and `emlxs_lpe12000_sli3`. The full image is conditionally materialized only when `EMLXS_FW_IMAGE_DEF` is defined; otherwise `emlxs_lpe12000_image` and `emlxs_lpe12000_size` collapse to zero.

## APIs and Data Surface

No C functions, structs, typedefs, or preprocessor APIs are declared in this line range. The effective API is the surrounding byte-array symbol:

- `emlxs_lpe12000_image[]`: byte-accurate firmware payload; this chunk is a middle segment of that array.
- `emlxs_lpe12000_size`: defined after the array as `sizeof (emlxs_lpe12000_image)`.
- `emlxs_fw_table`: built in `emlxs_fw.h` when `EMLXS_FW_TABLE_DEF` is set, with a `LPe12000_FW` entry that points at `emlxs_lpe12000_size`, `emlxs_lpe12000_image`, and the revision/Sli compatibility macros.

The consumer-facing C type is `emlxs_firmware_t`, whose fields carry the firmware id, size, image pointer, label, kernel/stub revision ids, and SLI revision identifiers. Driver code sees this chunk only as bytes reachable through that descriptor.

## Firmware Control Flow Visible in the Bytes

The byte stream is predominantly ARM-style instruction encoding. It contains repeated procedure-entry and procedure-exit patterns, including stack-frame setup/restoration sequences and many branch-with-link opcodes. Because symbol names and relocation metadata are not present in this header, these are not recoverable as named C routines from the source alone.

Visible behavior patterns in this interval include:

- Polling loops around memory-mapped state words, especially repeated reads/writes at offsets that appear as `0x30`, `0x34`, `0x3C`, `0x40`, `0x48`, `0x68`, `0x70`, `0xAC`, `0xB0`, `0x200`, `0x208`, `0x214`, `0x238`, `0x244`, `0x248`, `0x24C`, and `0x2A0`.
- Mode/command dispatch based on small numeric opcodes. The later part of the chunk compares values such as `0x01`, `0x02`, `0x03`, `0x11`, `0x16`, `0x17`, `0x19`-`0x1E`, `0x24`, `0x2A`, `0x37`, `0x38`, `0x3A`, `0x81`, `0x98`, `0x9A`, `0x9C`, and `0x9D`.
- Status/error returns encoded as immediate constants, including values that look like firmware status codes such as `0xD0`, `0xD1`, `0xD3`, `0xD5`, `0xD6`, `0xD7`, `0xD8`, `0xD9`, `0xF0`, `0xF2`, `0xF3`, and `0xF5`.
- Hardware-control sequences that set/clear bitfields in apparent control registers, including masks around `0x7F`, `0x80`, `0xFF`, `0x0100`, `0x0200`, and values written near offsets `0x238`, `0x23C`, `0x244`, `0x248`, `0x24C`, and `0x2A0`.
- Several routines copy small descriptors and buffers using load/store multiple patterns and bounded loops, commonly moving 4-byte or 8-byte chunks and updating length/count fields.

The chunk starts in the middle of an existing routine at firmware offset `0x0CF18` and ends in the middle of another routine at `0x136C0`; both routine boundaries cross chunk edges.

## State and Data Dependencies

The state manipulated here is firmware-private adapter state, not kernel C state. The bytecode appears to operate over:

- Adapter control/status register blocks, with repeated base constants that look like internal register-window selectors (`0x0Bxx`, `0x09xx`, `0x05xx`, `0x03xx`, and `0xC1xx`-style immediates).
- Queue or descriptor structures with fields at small fixed offsets (`0x08`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x28`, `0x30`, `0x34`, `0x38`, `0x40`, `0x44`).
- Firmware-visible progress flags and counters used for polling/timeout loops, including repeated tests for zero, one, two, and bit `0x08`.
- Interrupt or mailbox-like completion state, inferred from repeated status checks followed by register writes and branch-to-handler sequences.

At the C layer, this state is opaque. The host driver is responsible for selecting and downloading this payload through the Emulex firmware machinery; this chunk does not directly access illumos kernel APIs.

## Dependencies

Direct dependencies are structural:

- `fw_lpe12000.h` depends on `uint8_t` being available from includers and on the `EMLXS_FW_IMAGE_DEF` build-time switch.
- `emlxs_fw.h` includes this header when constructing the firmware table and maps this image to the `LPe12000_FW` enum id.
- `emlxs_hw.h` defines firmware-image parsing types such as `emlxs_fw_file_t` and `emlxs_fw_image_t`, plus firmware program type identifiers used by the broader download/update path.
- Driver declarations in `emlxs_extern.h` expose firmware operations such as `emlxs_fw_load`, `emlxs_fw_unload`, and `emlxs_fw_download`; these are the likely host-side paths that consume `emlxs_lpe12000_image`.

Runtime dependencies are hardware/firmware-specific: the byte stream assumes the LPe12000 adapter's processor architecture, register layout, mailbox/descriptor format, and SLI2/SLI3-compatible firmware layout. The source tree does not provide symbolic source for those internals here.

## Risks and Maintenance Notes

- This chunk is opaque binary firmware embedded in a C header. Normal source review cannot prove semantic correctness, memory safety, or hardware side effects.
- Any byte edit is high risk. Alignment, offsets, branch targets, checksums/signatures, and revision metadata may all depend on exact byte positions.
- The full image is large (`0x75C0C` bytes in the array terminator comment), so chunked review must preserve ordering. This interval is not independently meaningful without previous and following chunks.
- Licensing differs from standard illumos CDDL text: the parent header says use/copy/distribution are under Emulex `License 2` in `LICENSE.txt`. Redistribution and modification risk should be evaluated against that license.
- Because the image is compiled into kernel/driver firmware support when `EMLXS_FW_IMAGE_DEF` is enabled, stale or corrupt bytes can affect adapter initialization or firmware download rather than only build behavior.

## Cross-Chunk References

- Previous chunks define the header guard, firmware label/revision macros, the `emlxs_lpe12000_image[]` declaration, the image header, and the earlier firmware routines that branch into this interval.
- This chunk begins mid-stream at `0x0CF18`, so the active routine's entry state is in the previous chunk.
- This chunk ends at `0x136C0` with a branch/call sequence still in progress; the callee/continuation and remaining firmware routines are in later chunks.
- Later chunks close `emlxs_lpe12000_image[]`, define `emlxs_lpe12000_size`, provide the zero-image fallback for builds without `EMLXS_FW_IMAGE_DEF`, and close the header guard.