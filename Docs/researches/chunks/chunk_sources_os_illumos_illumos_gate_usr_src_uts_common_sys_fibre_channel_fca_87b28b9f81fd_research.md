# Chunk Research: `fw_lpe11002.h` Lines 36515-39832

This chunk is a contiguous slice of the generated `emlxs_lpe11002_image[]` firmware byte array for the Emulex LPe11002 Fibre Channel adapter in illumos `emlxs`. It covers source lines 36515-39832, firmware offsets `0x47448` through the row beginning at `0x4DBF0`. The range is in `sources/os/illumos/illumos-gate`, which is included by `Docs/research_subset_a.md`.

## APIs And Host Surface

- No C functions, structs, typedefs, enums, macros, or host-callable illumos APIs are declared in this range.
- The only C-visible entity is the enclosing firmware image array, conditionally emitted by file-level `EMLXS_FW_IMAGE_DEF` machinery outside this chunk.
- Host code treats these bytes as opaque adapter firmware to download; it cannot link to or type-check the firmware-internal routines visible in the byte stream.
- The surrounding header and firmware table metadata, not this line range, define the driver-facing firmware identity, size, version, and adapter selection contract.

## Firmware Control Flow

- The chunk opens with descriptor/table bytes from `0x47448` to roughly `0x47597`, continuing the table region that began in the previous chunk.
- Embedded diagnostic strings appear at `0x47598`-`0x475E7`: `TIME: %08x  %s`, `%08x:`, `%08x %08x`, `%08x %08x\n`, and `Rcverr Frm %x. Idx %x.\n`.
- Executable ARM-style firmware resumes at `0x475E8`, with register-save prologues, returns, conditional branches, branch-with-link calls, PC-relative literal loads, and copy sequences.
- Early routines around `0x475E8`-`0x47C20` touch fields near offsets `+0x04`, `+0x24`, `+0x65`, `+0x68`, `+0x71`, `+0x90`-`+0x9B`, `+0x140`, `+0x144`, `+0x1FC`, `+0x2C8`, `+0x2D8`, `+0x370`, `+0x380`, and `+0x3C0`.
- Around `0x4A760`-`0x4A940`, a branch-table-like path classifies a selector and updates fields such as `+0x4E`, `+0x50`, `+0x54`, `+0x56`, `+0x57`, `+0x58`, `+0x6C`, and counters near `+0x2A8`-`+0x2B8`.
- Around `0x4A940` onward, routines compare request/status words, classify constants such as `0x0102`, `0x0321`, `0x0401`, `0x0405`, `0x0407`, `0x0481`, and `0x0485`, and set response/status byte values like `0x10`, `0x20`, `0x40`, `0x50`, `0x60`, `0xD0`, `0xE0`, and `0xF0`.
- The tail around `0x4D410`-`0x4DBF0` performs exchange/buffer descriptor updates, copying nested record words and writing byte state fields at `+0x07`, `+0x08`, `+0x09`, `+0x0A`, `+0x0B`, `+0x0F`, `+0x26`, `+0x27`, and `+0x3C`.
- The final row at `0x4DBF0` is still inside executable firmware and continues into later chunks.

## State And Data

- Firmware-side state is implicit in untyped offsets. Frequently visible offsets include `0x04`, `0x07`, `0x08`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x26`, `0x27`, `0x2C`, `0x30`, `0x38`, `0x3C`, `0x40`, `0x44`, `0x4E`, `0x50`, `0x54`, `0x56`, `0x57`, `0x58`, `0x64`, `0x65`, `0x68`, `0x6A`, `0x6C`, `0x70`, `0x71`, `0x90`-`0x9B`, `0xBC`, `0x140`, `0x144`, `0x1FC`, `0x2A8`-`0x2B8`, `0x2C8`, `0x2D8`, `0x370`, `0x380`, and `0x3C0`.
- Descriptor/table records at the beginning likely describe firmware register or memory regions shared with the previous chunk’s descriptor block.
- The diagnostic strings show support for firmware timestamped dumps and receive error reporting by frame/index.
- Later code appears to maintain per-frame, per-exchange, or queue-entry state.

## Dependencies

- Build-time dependency: exact byte order, row order, commas, and alignment must remain unchanged so the array reconstructs the vendor firmware image.
- Host dependency: the `emlxs` firmware loader and file-level metadata outside this chunk select and download this image as an LPe11002 firmware payload.
- Runtime dependency: these bytes assume the LPe11002 adapter CPU, memory map, register layout, SLI/Fibre Channel firmware ABI, and on-card state layouts.
- Control-flow dependency: many calls and branches target helpers outside this chunk in both earlier and later image ranges.

## Risks

- Any byte edit can corrupt executable instructions, descriptor tables, literal pools, branch targets, embedded strings, or hardware register programming.
- Normal C compilers and static analyzers can only verify initializer syntax, not firmware memory safety, concurrency, protocol sequencing, or hardware timing.
- The receive/error and exchange update paths visible here affect Fibre Channel frame processing.
- The line range starts in table data and ends mid-routine, so isolated review cannot prove full initialization, cleanup, or error-path behavior.
- The firmware is vendor-supplied binary data embedded as C source; provenance, license, and device compatibility risks are file-level concerns inherited by this chunk.

## Cross-Chunk References

- Previous chunk ends at source line 36514 / firmware offset `0x47447`; its descriptor/table region continues directly into this chunk at `0x47448`.
- This chunk resumes executable firmware after the initial descriptor and string area at `0x475E8`.
- Calls and branches repeatedly target routines before `0x47448`.
- Forward branches and helper calls leave this chunk, especially from the receive/exchange handling paths near the tail.
- The next chunk begins after the row at `0x4DBF0` and is needed to complete the routine active at this boundary.