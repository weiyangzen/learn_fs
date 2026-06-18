# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 23244-26561

This chunk is inside the illumos `emlxs` Fibre Channel adapter firmware headers covered by `Docs/research_subset_a.md`. It is not normal C implementation code; it is a contiguous slice of the embedded `emlxs_lp11002_image[]` byte array for LP11002-S adapter firmware.

The range covers 3,318 source rows, from firmware offset `0x2D590` through `0x33D3F`. Surrounding metadata identifies the full image as `LP11002-S: v2.82a4 (bf282a4.all)`, with kernel/stub/SLI constants and total image size `0x8DCB8`.

## APIs And Surface

No C functions, structs, typedefs, or callable kernel APIs are defined here. The only host-visible surface is positional firmware data inside `static uint8_t emlxs_lp11002_image[]`, emitted under `EMLXS_FW_IMAGE_DEF`.

The practical contract is byte-exact firmware identity, alignment, offsets, and size. Internal routines are visible only through ARM instruction patterns and embedded strings, not through symbols.

## Control Flow

The chunk is dense ARM-style firmware code mixed with literal pools and short diagnostics. Repeated prologue/epilogue patterns such as `E9 2D`, `E9 1B`, `E8 BD`, and `E1 A0 F0 0E` indicate many firmware-internal helpers.

Key visible regions:

- `0x2D590` starts mid-routine, loading literal addresses around `0x00083064`-`0x00083070`, testing status values, masking low bits, and writing merged fields.
- `0x2D680` begins a larger initialization/copy path, writes byte code `0x46` at `+0x07`, sets a byte at `+0x78`, calls helpers, and copies blocks with load/store-multiple loops.
- `0x2D718` starts validation and bit-propagation logic over context/status fields.
- `0x2DF98` embeds `DWNL %08x`, suggesting download-state logging.
- `0x2F550`-`0x2FA08` is a dense dispatcher/state-machine area comparing command/status bytes and branching to external handlers.
- `0x32820` embeds diagnostics including `trc dup @%x` and `S/E/XCB %08x`.
- `0x32D28` embeds `Corrupted frame sent %02x` and `Cmd IOCB`.
- `0x33868` handles a wait/buffer path with `Wait Buf %x` and command/status codes such as `0xA0`, `0xA1`, `0xA2`, `0xA3`, and `0xA7`.
- `0x33A78` embeds `Toss %x`, adjacent to discard/marking logic.
- `0x33CE0` begins a routine that continues beyond this chunk.

## State And Dependencies

Repeated field offsets suggest firmware objects for adapter context, exchanges, buffers, IOCBs, and queues. Common offsets include `+0x04`, `+0x06`, `+0x07`, `+0x08`, `+0x0C`, `+0x14`, `+0x18`, `+0x1C`, `+0x20`, `+0x24`, `+0x28`, `+0x2C`, `+0x30`, `+0x34`, `+0x38`, `+0x4C`, `+0x6C`, `+0x70`, `+0x78`, `+0x80`, `+0xB8`, and larger global offsets such as `+0x260`, `+0x2F0`, `+0x350`, `+0x370`, and `+0x700`.

Visible diagnostics point to download, timeout, abort, ABTS/XRI/RPI, response-ring backpressure, exchange-control-block, frame, IOCB, wait-buffer, and discard paths.

Runtime dependencies are the illumos `emlxs` firmware loader, compatible LP11002 hardware, SLI1/SLI2/SLI3 firmware conventions, and the adapter’s on-card memory/register layout.

## Risks

This is opaque vendor firmware. Any byte edit, insertion, deletion, byte swap, string change, or row truncation can corrupt branch targets, literal pools, diagnostics, or adapter behavior. Normal C review cannot validate memory safety or protocol correctness. The chunk also starts and ends mid-routine, so invariants are incomplete without neighboring chunks.

## Cross-Chunk References

The previous chunk contains the start of the routine active at `0x2D590`. The next chunk continues the routine beginning around `0x33CE0`, after the final visible comparisons at `0x33D38`. File-level merge should connect this report to LP11002 metadata, the full `emlxs_lp11002_image[]` declaration, total size `0x8DCB8`, and the external `emlxs` firmware table/adapter-selection logic.