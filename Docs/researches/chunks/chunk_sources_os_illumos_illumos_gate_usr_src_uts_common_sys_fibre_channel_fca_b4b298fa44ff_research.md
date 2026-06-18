# Chunk Research: fw_lpe11002.h Lines 46469-49786

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h`

Scope: subset A from `Docs/research_subset_a.md`. I read the full requested line range. Adjacent context was used only to identify the enclosing declaration and neighboring chunk boundaries.

## Overview

This chunk is entirely inside `static uint8_t emlxs_lpe11002_image[]`, the embedded firmware byte image for the Emulex LPe11002-S Fibre Channel adapter. It is not host-executed illumos C code. The range contributes 3,318 eight-byte initializer rows, covering firmware offsets `0x5AB58` through `0x61307` inclusive.

The bytes are mostly ARM-like firmware instructions plus embedded diagnostic strings. The host compiler only preserves these bytes in the driver image when `EMLXS_FW_IMAGE_DEF` is defined. Runtime behavior described below is therefore inferred from firmware byte patterns, fixed offsets, branches, and visible strings, not from source-level symbols.

## APIs And Host-Visible Surface

- No C functions, structs, typedefs, enums, or macros are defined in this line range.
- The only C-visible object touched is the enclosing `emlxs_lpe11002_image[]` array. File-level metadata outside this chunk defines the label `LPe11002-S: v2.82a4 (zf282a4.all)`, SLI entry constants, and the conditional image/size contract used by the `emlxs` firmware table.
- Driver code should not call into this range directly. The driver treats it as firmware payload selected for LPe11002-class adapters and downloaded to the HBA.

## Control Flow Visible In The Firmware

- The chunk starts mid-routine at `0x5AB58`; preceding register setup and entry conditions are in the prior chunk.
- Visible paths cover link/port setup, loop monitor transitions, old-port handling, LIP F7/F8 receipt, open initialization, ARB(F0), RRQ/recovery requests, exchange-control blocks, buffer ownership, and free-list state.
- Embedded diagnostics include `IntL EXP=%x`, `BARJT %x`, `BAACC buf %x`, `ABTSbuf %x`, `RJT buf %x`, `XCB 0: Can't start xchg`, `Try_OLDP`, `Try_LOOP`, `Acquire Sync %08x`, `ISSUE LPRQ_INIT`, `TO_LOOP1`, `LOOP ACTIVE!!!`, `LOSSSYNC`, `Begin RRQ %x->rpi %02x`, `Call new cmd for RRQ sid %08x xid %08x`, `ZXCB OK frame.`, `RCVD_LIP_F8`, `lipf8_rcvd`, `Unknown port_state=%x`, `Loop Phase=%x`, `To OPEN_INIT Due To: lipf7_rcvd`, `ARBF0`, and `Ignored(Not a LISM`.
- The chunk ends mid-path at `0x61307`; the `Ignored(Not a LISM` diagnostic/control path continues in the next chunk.

## State And Data

- Host-side state is immutable static firmware data. No illumos kernel state is mutated by the C compiler when this chunk is compiled.
- Firmware-side state is heavily offset based, with repeated accesses to small fields such as `+0x04`, `+0x06`, `+0x07`, `+0x0C`, `+0x14`, `+0x18`, `+0x1C`, `+0x2C`, `+0x30`, `+0x6C`, `+0x70`, `+0x73`, `+0x74`, `+0x78`, `+0x79`, `+0x7C`, `+0x98`, `+0xA0`, `+0xB0`, `+0xC4`, `+0xCC`, `+0xD3`, `+0xDB`, and larger offsets including `+0x114`, `+0x128`, `+0x140`, `+0x154`, `+0x160`, `+0x170`, `+0x17C`, `+0x184`, `+0x204`, `+0x244`, `+0x260`, `+0x270`, `+0x2C0`, `+0x2D8`, `+0x308`, `+0x374`, `+0x638`, and `+0x660`.
- Visible state values include port/link phase constants such as `0x80`, `0x90`, `0xA0`, `0xB0`, `0xC0`, `0xE0`, and `0xF0`.

## Dependencies

- Compile-time dependency: this chunk is meaningful only within `fw_lpe11002.h` and only when the enclosing `emlxs_lpe11002_image[]` initializer is emitted under `EMLXS_FW_IMAGE_DEF`.
- Driver dependency: external `emlxs` firmware-table code consumes the complete image, size, label, and SLI metadata. This chunk has no standalone consumer.
- Firmware runtime dependencies include the LPe11002 adapter processor, memory map, hardware registers, ring/queue layout, mailbox or SLI control structures, FC-AL loop semantics, LIP/LISM/LPRQ/RRQ frame formats, and firmware-private control blocks.
- Many branch/call targets leave this line range. The routines here depend on common helpers and state setup from earlier chunks and continue into later chunks.

## Risks

- This is opaque vendor firmware. Any byte-level edit can break branch targets, literal pools, checksums or implicit layout assumptions, hardware register sequencing, FC loop timing, or adapter compatibility.
- The byte array uses exact row order and commas as C initializer syntax; accidental insertion/deletion shifts every subsequent firmware offset.
- Diagnostic strings are interleaved with executable bytes and literal pools. Treating them as ordinary C strings or deleting them would corrupt firmware code/data layout.
- The chunk is split mid-routine at both boundaries. Any source-level review must avoid over-attributing standalone semantics to the first or last visible rows.

## Cross-Chunk References

- Previous chunk lines `43151-46468` cover offsets `0x543A8`-`0x5AB57` and end immediately before this range. It contains the entry/setup context for the helper sequence that continues at `0x5AB58`.
- This chunk begins at `0x5AB58`, not a standalone function boundary.
- This chunk ends at row `0x61300`, byte `0x61307`, in the middle of the `Ignored(Not a LISM` diagnostic/control path.
- Next chunk lines `49787-53104` start at `0x61308` and continue the same loop initialization / LPRQ / ARBF0 handling region.
- File-level merge should record this as one opaque firmware-image segment, not as host C logic, and should connect it to the `emlxs_lpe11002_image[]` metadata and firmware-table consumer described by earlier chunks.