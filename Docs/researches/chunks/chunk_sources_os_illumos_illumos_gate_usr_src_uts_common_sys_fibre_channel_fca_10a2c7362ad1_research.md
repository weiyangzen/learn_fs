# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 1-3334

## Scope And Artifact Role

This chunk is the first ordered slice of the oversized Emulex LPe11002 firmware header. The C-visible part defines include guards, C++ linkage, firmware identity constants, and, when `EMLXS_FW_IMAGE_DEF` is enabled, the beginning of `static uint8_t emlxs_lpe11002_image[]`. The array is a raw controller firmware image, not normal host-executed C code.

Host-visible exports in this chunk:

- `emlxs_lpe11002_label`: `"LPe11002-S: v2.82a4 (zf282a4.all)"`.
- `emlxs_lpe11002_kern`: `0xFFE01250`.
- `emlxs_lpe11002_stub`: `0x02E82894`.
- `emlxs_lpe11002_sli1`: `0x06E12893`.
- `emlxs_lpe11002_sli2`: `0x07E12894`.
- `emlxs_lpe11002_sli3`: `0x0BE12894`.
- `emlxs_lpe11002_sli4`: `0x00000000`, indicating no SLI4 image/version in this firmware descriptor.
- `emlxs_lpe11002_image[]`: defined only under `EMLXS_FW_IMAGE_DEF`, 8-byte aligned with `#pragma align 8`.

The chunk covers source lines 1-3334, corresponding to firmware byte offsets roughly `0x00000` through `0x06760`. The complete file is much larger, so this report only covers the visible prologue and early firmware code/data.

## Host Integration And Dependencies

The immediate host dependency is `EMLXS_FW_IMAGE_DEF`. If it is not defined, this chunk contributes only metadata macros; the image body is omitted and later file footer logic defines the image pointer/size as zero. When `EMLXS_FW_IMAGE_DEF` is defined, this chunk starts the embedded image that `emlxs_fw.h` places in an `emlxs_firmware_t` table entry for `LPe11002_FW`.

`emlxs_fw.h` includes `fw_lpe11002.h` and builds an `EMLXS_FW_TABLE` entry using `emlxs_lpe11002_size`, `emlxs_lpe11002_image`, `emlxs_lpe11002_label`, and the version constants. `emlxs_adapters.h` maps Oracle/Emulex Zephyr DC LPe11002-S adapter entries to `LPe11002_FW`, with SLI2 and SLI3 support masks. This makes the header a firmware payload selected by adapter identity, not an API surface called directly by driver C functions.

## Control Flow And State

The host-side C control flow is trivial: metadata macros are always available; the image definition is included conditionally under `EMLXS_FW_IMAGE_DEF`. There are no host-callable C functions in this chunk.

The firmware-internal control flow is substantial:

- Early vectors branch into common initialization/dispatch routines.
- Around `0x004A0`, selector stubs for values `1..0x10` funnel into shared code.
- Around `0x013B8`, code saves/restores registers, masks mode bits, and manipulates fixed firmware offsets such as `0x734`, `0x764`, `0x768`, and `0x7A4`.
- Around `0x02E18` and `0x02EC8`, jump tables dispatch command or runtime handlers.
- Around `0x03708`-`0x038D8`, byte patterns indicate memory/string/list helpers.
- Around `0x038E0`-`0x047D8`, allocator/pool management is visible through block metadata operations and diagnostics.
- Around `0x05F80` through the chunk end, printf-like parser/formatter logic handles flags and conversions including `%`, `+`, space, `#`, `-`, `0`, `c`, `d`, `e`, `f`, `g`, `i`, `l`/`L`, `n`, `o`, `p`, `s`, `u`, `x`, and `X`.

Visible firmware state includes fixed global/control areas, queue/list nodes, allocator metadata, character classification tables, and diagnostic strings such as `"Unknown Error"`, `"Divide by zero"`, `"malloc failed"`, `"free failed"`, `"realloc failed, (bad user block)"`, and `"Couldn't write "`.

## Risks And Cross-Chunk References

This header embeds an opaque firmware image. Small byte edits are high risk because offsets, branch targets, checksums/signatures, and device compatibility may be implicit. The metadata constants must remain synchronized with the binary image and with the `emlxs_fw.h` table entry. `emlxs_lpe11002_sli4` is zero, so consumers must not infer SLI4 support.

This chunk ends mid-routine at offset `0x06760`; the formatter/hex emission logic continues in the next chunk. Later chunks must resolve branch-table targets outside this range, confirm the final `emlxs_lpe11002_size` definition, and check for image trailer/checksum/download metadata.