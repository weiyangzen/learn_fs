# Chunk Research: `fw_lpe11000.h` Lines 26561-29878

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h`

Scope: learn_fs subset A, ordered chunk 9 of the illumos `emlxs` Emulex LPe11000 firmware header.

## Chunk Identity

This chunk is a contiguous middle slice of `static uint8_t emlxs_lpe11000_image[]`, not normal driver C source. The requested range was read completely and spans firmware image offsets `0x33D38` through `0x3A4E0` in the embedded LPe11000-S firmware image `v2.82a4 (zd282a4.all)`.

The line range begins in the middle of ARM firmware code continued from chunk 8 and ends in the middle of another firmware routine. Adjacent context confirms the enclosing array and that the header-level exported objects remain `emlxs_lpe11000_image[]` and `emlxs_lpe11000_size` when `EMLXS_FW_IMAGE_DEF` is defined.

## APIs And Host-Visible Surface

No C functions, structs, macros, or illumos kernel APIs are declared inside this chunk. Its host-visible contract is the exact byte sequence within the larger firmware image consumed by the `emlxs` firmware download path.

The relevant public symbols are outside this line range: `emlxs_lpe11000_label`, firmware entry/address constants, `emlxs_lpe11000_image[]`, and `emlxs_lpe11000_size`. The host driver treats this region as opaque adapter firmware; it does not call the routines visible here as C functions.

## Embedded Control Flow

The byte stream is ARM instruction/literal data. Visible patterns include function prologues/epilogues, branch/link calls to routines before and after this chunk, PC-relative string/literal references, and fixed-offset loads/stores into firmware-private control blocks.

Major visible firmware themes:

- Exchange and buffer handling around strings such as `BARJT %x`, `BAACC buf %x`, `ABTSbuf %x`, `RJT buf %x`, `XCB 0: Can't start xchg`, `ZXCB %08x`, and `ZXCB OK`.
- Link and loop/ALPA handling near the end of the chunk: `LIRP`, `LILP`, `XMT_CLS`, `CLS`, `Master BitMap`, `BitMap[%x]=%08x`, `#of ALPA=%x`, `PosMap=>%02x`, `No Position Map`, and `LINK IS UP!`.
- Receive/interrupt logic visible through `Rcvd=>...`, `Rcvd Frame called`, and `no interrupt`.
- Transmit/link-idle timeout handling via `Timeout TX Never IDLE`.

Several routines appear to decode frame or exchange status bytes, allocate or check buffer/control-block state, update queue or link flags, and branch to common handlers for abort/reject/close/link-completion paths. Because this is a binary blob, exact behavior is inference from strings, constants, and access patterns.

## State And Dependencies

State is firmware-private and represented by hard-coded offsets from base registers. Common byte fields such as `0x06`, `0x07`, `0x08`, `0x0a`, `0x70`, `0x74`, `0x79`, `0xad`, and `0xdb` look like status/state flags. Word fields such as `0x0c`, `0x18`, `0x1c`, `0x24`, `0x28`, `0x30`, `0x98`, `0xb0`, `0xb4`, `0xbc`, `0xcc`, and `0xd4` look like queue pointers, register mirrors, counters, exchange identifiers, or link-control words.

The chunk depends on the exact LPe11000/Zephyr adapter firmware ABI, ARM execution environment, SLI/Fibre Channel exchange semantics, LIRP/LILP loop initialization/position-map handling, ALPA accounting, receive-frame and interrupt processing, and the illumos `emlxs` loader preserving image alignment, byte order, size, and version compatibility.

## Risks

This region is executable device firmware embedded as C data. Any byte edit, dropped initializer value, reordered line, or mistaken regeneration can change adapter behavior in link bring-up, loop initialization, exchange lifecycle, abort/reject handling, receive processing, interrupts, or DMA-visible queue state.

Static source review cannot verify provenance or memory safety of this firmware. Diagnostic strings are useful anchors, but disassembly from the wrong offset or treating literal pools as code can produce misleading conclusions.

## Cross-Chunk References

Chunk 8 (`fw_lpe11000.h` lines 23243-26560) ends immediately before this range and already reports `IntL EXP`, abort, blocked response ring, BIU/receive queue, and DMA reset/recovery diagnostics. This chunk continues that firmware control-flow region at `0x33D38`.

The next ordered chunk should begin at line 29879 and continue from firmware offset `0x3A4E8`; the available later same-file report for lines 33197-36514 starts at offset `0x40C98`, so line range `29879-33196` is an intervening chunk not covered here.