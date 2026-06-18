# Chunk Research: `fw_lpe11002.h` Lines 49787-53104

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h`

Scope note: this chunk is entirely inside `static uint8_t emlxs_lpe11002_image[]`, the embedded Emulex LPe11002 adapter firmware image. It contains firmware bytes and byte-row comments, not illumos host-executed C functions.

## Chunk Extent

- Source lines read completely: 49787-53104.
- Firmware image offsets covered: byte row `0x61308` through byte row `0x67AB0`, ending at byte `0x67AB7`.
- Byte rows in this chunk: 3,318 rows, 26,544 image bytes.
- Whole-file context identifies the image as `emlxs_lpe11002_image[]`, guarded by `EMLXS_FW_IMAGE_DEF`, aligned with `#pragma align 8`, and later closed with size `0x8F3A8` bytes.
- This chunk starts after earlier executable firmware code has already entered a link/loop handling path and ends in a zero-filled region. It is not aligned to a C or firmware function boundary.

## APIs and Integration Surface

- No new host-visible APIs, macros, structs, functions, or typedefs are defined in this line range.
- The only C object being extended is the file-level firmware byte array `emlxs_lpe11002_image[]`.
- `emlxs_fw.h` includes this header and places `emlxs_lpe11002_image`, size, label, and version constants in the `LPe11002_FW` firmware-table entry. Host firmware load/show/download paths operate on that table entry rather than on any API in this chunk.

## Firmware Control Flow Visible

- The first portion is dense ARM-like adapter firmware code: prologues/returns, unconditional branches, branch-with-link helper calls, and literal/object-relative loads/stores.
- Embedded strings identify Fibre Channel loop/link initialization and recovery behavior: `IAM_MASTER`, `XMT_ARBF0`, `=FL_PORT`, `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `XMT_CLS`, `XMT_LISM`, `=IGNORED`, `XRCV_`.
- Diagnostic strings show firmware decision and timeout paths: `Master BitMap`, `#of ALPA=%x`, `No Position Map`, `LINK IS UP!`, `Timeout TX Never IDLE`, `Never Sync`, `FTXQ int never set`, `Issue LipF7 Reset to AL_PA=%x`, `LIPF8s > 2 secs`, `LPTOV Timeout`.
- The implied firmware flow handles AL_PA/master selection, position-map handling, loop primitive transmit/receive, LIPF7/LIPF8 detection, timeout recovery, and link reinitialization.
- Around `0x66E10`, the bytes shift into compact tables and big-endian-looking constants. From about `0x66EB0` onward, the chunk is mostly zero-filled reservation/padding with sparse nonzero constants.

## State, Dependencies, Risks

- Host-side state is only the immutable byte-array initializer; no host locks, callbacks, globals, or control flags are introduced.
- Firmware-side state is opaque, but repeated offsets suggest private adapter context fields related to link state, queues, synchronization, interrupts, AL_PA selection, and loop timeouts.
- Dependencies are the firmware-image build path via `EMLXS_FW_IMAGE_DEF`, the `emlxs_fw.h` firmware table, and the Emulex LPe11002 adapter CPU/memory/register/SLI ABI.
- Risk is high opacity: byte order and positions are contractual. Reformatting, deleting apparent padding, or editing strings/tables can corrupt branch targets, literal pools, firmware diagnostics, or hardware behavior.
- The zero-filled tail should not be treated as removable dead data; it may be reserved image space, alignment, segment padding, or BSS-like initialization data.

## Cross-Chunk References

- Previous chunks contain the file preamble, metadata macros, image start, and earlier code that can branch/call into this region.
- This chunk begins mid-routine at `0x61308`; adjacent preceding bytes include `Ignored(Not a LISM)`, so the first visible bytes are not a standalone entry point.
- Later chunks continue from `0x67AB8`; the final per-file report should merge all chunks before making whole-image claims about layout, reachability, or unused padding.