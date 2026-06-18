# Chunk Research: fw_lpe11002.h lines 56423-59740

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h`

Scope note: this chunk is entirely inside `static uint8_t emlxs_lpe11002_image[]`, the embedded firmware image for the Emulex LPe11002-S Fibre Channel adapter. It is not host-executed C logic. The C compiler only stores these bytes in the driver image when `EMLXS_FW_IMAGE_DEF` is enabled.

## Chunk Extent

- Source lines read completely: 56423-59740.
- Firmware image offsets covered: `0x6E268` through the eight-byte row beginning at `0x74A10`, ending at byte `0x74A17`.
- Byte span represented: `0x67B0` bytes, 26,544 bytes total.
- Adjacent metadata identifies the full image as `emlxs_lpe11002_image[]` with size `0x8F3A8` bytes and label `LPe11002-S: v2.82a4 (zf282a4.all)`.

## APIs and Integration Surface

- This chunk exports no C functions, macros, structs, or callable APIs of its own.
- Its only C-visible surface is the containing array `emlxs_lpe11002_image[]`.
- The image is referenced through `emlxs_fw.h` as the `LPe11002_FW` entry in `EMLXS_FW_TABLE`.
- Host-side driver declarations visible in adjacent headers include `emlxs_fw_load()`, `emlxs_fw_unload()`, `emlxs_fw_download()`, `emlxs_fw_table[]`, and `emlxs_fw_file_t` / `emlxs_fw_image_t`.

## Firmware Control Flow Visible

- The byte stream is consistent with big-endian ARM instructions: register-save prologues, returns, unconditional branches, branch-with-link calls, and pointer-relative loads/stores.
- The first rows continue a routine from the previous chunk, masking/setting a control word at offset `0x0C` and mirroring fields around `0x30`, `0x80`, `0x88`, `0x260`, and `0x264`.
- Several local routine boundaries appear, including state update/copy logic around `0x6E328`, `0x6E670`, `0x6E7A8`, `0x6E7E0`, and `0x6E950`.
- The late section around `0x74590` begins a larger bit-packing path over fields from `0x20` through `0x60`; it continues beyond this chunk.

## State and Dependencies

The visible state is pointer-relative firmware state: recurring offsets include control words at `0x0C`-`0x2C`, status bytes around `0x30`-`0x3C` and `0x70`-`0x73`, nested pointers/queues at `0x64`-`0x88`, and firmware-private areas such as `0x260`, `0x264`, `0x2A4`, `0x2A8`, and `0x2AC`.

Dependencies are the containing firmware table machinery in `emlxs_fw.h`, metadata structs in `emlxs_hw.h`, and host download/load entry points declared in `emlxs_extern.h`. Runtime dependencies are the adapter CPU, memory map, register layout, and firmware ABI.

## Risks and Cross-Chunk References

- A single-byte change can alter firmware behavior, branch targets, hardware sequencing, or image integrity.
- Endianness matters: the bytes appear to encode big-endian ARM instructions.
- The chunk starts and ends mid-control-flow. Previous-chunk context is needed before `0x6E268`; next-chunk context is needed after `0x74A10`.
- Final per-file analysis should merge all chunks before drawing conclusions about firmware layout, embedded tables, branch reachability, or integrity.