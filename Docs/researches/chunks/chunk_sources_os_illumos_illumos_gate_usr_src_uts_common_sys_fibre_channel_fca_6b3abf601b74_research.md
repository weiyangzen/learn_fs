# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 59741-63058

## Scope And Artifact

This report covers chunk 19 of the oversized `fw_lpe11000.h` firmware header, within learn_fs subset A as defined by `Docs/research_subset_a.md`. I read the complete requested line range `59741-63058` and used adjacent context only to confirm the enclosing header, firmware table integration, and chunk boundaries.

The file is an Emulex LPe11000 firmware image header, not normal illumos driver implementation code. This chunk is inside `static uint8_t emlxs_lpe11000_image[]`, covering firmware offsets `0x74A18` through `0x7B1C7`. It contributes 26,544 bytes to the full `0x8A5CC`-byte image and ends mid-firmware routine.

## APIs And Host Surface

No C functions, structs, typedefs, constants, or illumos kernel APIs are declared in this range. The host-visible artifact is only the bytes contributed to `emlxs_lpe11000_image[]`.

Outside this chunk, `emlxs_fw.h` builds the `LPe11000_FW` descriptor from `emlxs_lpe11000_size`, `emlxs_lpe11000_image`, label `LPe11000-S: v2.82a4 (zd282a4.all)`, and kernel/stub/SLI metadata. The metadata declares SLI1/2/3 values and `emlxs_lpe11000_sli4 == 0`.

## Firmware Control Flow

The bytes are mostly ARM-style big-endian executable firmware, visible through branch, load/store, compare, and prologue/epilogue opcode patterns.

- `0x74A18-0x74AD8` completes a status/polling path, checking pointer-like fields around `0x2C` and `0x20`, using literal address `0x0009687C`, and returning boolean-like `0`/`1`.
- `0x74AE0-0x74EA0` is a larger dispatcher/state handler comparing state values including `0x22`, `0x34`, `0x35`, `0x37`, `0x3A`, `0x45`, `0x47`, `0x80`, `0x82`, `0x83`, and `0x8B`.
- `0x74EA8-0x74FA0` processes state values around `0x23`, `0x81`, `0x85`, `0x89`, and `0x8A`, updating fields at `0x30`, `0x3C`, `0x6C`, and `0x07`.
- `0x74FA8-0x75200` manages descriptor-like objects through fields around `0x260`, `0x264`, `0x80`, `0x84`, and `0x88`.
- `0x75200-0x77D00` contains dense helper logic for queue/exchange manipulation, descriptor copying, counter updates, and list/ring traversal.
- `0x79600-0x7AB80` includes a large command/status dispatcher, incrementing counters around `0x10C`, `0x110`, `0x168`, and `0x17C`, and setting flag bytes around `0xAF` and `0xDA`.
- `0x7AB88-0x7B0B0` manipulates global queue/list state around `0x2C0`-`0x2CC`, `0xFC`, `0x100`, `0x104`, `0x148`, `0x358`, and `0x464`.
- `0x7B0C0-0x7B1C0` begins low-level bit/line helper logic that continues into the next chunk.

## State And Data

Visible high-activity firmware-private offsets include byte fields `0x06`, `0x07`, `0x08`, `0x0A`, `0x21`, `0x25`, `0x26`, `0x33`, `0x35`, `0x36`, `0x39`, `0x3C`, `0x73`, `0x87`, `0xA0`, `0xA7`, `0xAF`, `0xDA`, and `0xF2`.

Frequent word/pointer fields include `0x0C`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x28`, `0x2C`, `0x30`, `0x34`, `0x38`, `0x40`, `0x4C`, `0x50`, `0x58`, `0x6C`, `0x70`, `0x74`, `0x80`, `0x84`, `0x88`, `0x8C`, `0xFC`, `0x100`, `0x104`, `0x108`, `0x10C`, `0x110`, `0x148`, `0x168`, `0x17C`, `0x1B0`, `0x260`, `0x264`, `0x270`, `0x2C0`-`0x2CC`, `0x358`, and `0x464`.

The range exposes no meaningful embedded ASCII diagnostic strings; it is primarily executable bytes and literal-pool words.

## Dependencies And Risks

Host-side dependencies are `uint8_t`, the file-level `#pragma align 8(emlxs_lpe11000_image)`, and the `EMLXS_FW_IMAGE_DEF` build split. Firmware-side dependencies are opaque hardware contracts: controller CPU architecture, byte order, memory map, register layout, adapter queues, and SLI1/2/3 behavior.

The main risk is byte integrity. Any edit, row deletion, endian change, formatter rewrite, or misplaced comma can corrupt firmware instructions or data while leaving the C header syntactically valid. The chunk starts and ends mid-control-flow, so adjacent chunks are required for complete invariants.

## Cross-Chunk References

Previous chunk line `59740` ends at firmware offset `0x74A10`; this chunk starts at `0x74A18` and inherits active control flow. Next chunk line `63059` starts at `0x7B1C8` and continues the routine begun at the end of this chunk. Earlier and later chunks provide the array declaration, metadata macros, final size macro, and fallback definitions.