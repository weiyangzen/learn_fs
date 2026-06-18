# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 66377-69694

## Scope

This chunk is a contiguous slice of the generated Emulex LPe11000-S firmware image embedded in `fw_lpe11000.h`. It covers source lines 66377-69694, firmware offsets `0x81978` through `0x88120`, or 26,544 encoded firmware bytes. The file belongs to the illumos source tree included by `Docs/research_subset_a.md`.

The content is not C implementation logic with named functions. It is a byte array containing ARM-style firmware instructions, branch tables, literal addresses, and embedded firmware diagnostic strings. The report therefore describes the observable firmware behavior and host-facing data surface rather than C-level APIs.

## APIs and Entry Points

- Host-visible API surface: this chunk contributes bytes to `static uint8_t emlxs_lpe11000_image[]` when `EMLXS_FW_IMAGE_DEF` is enabled. It defines no C functions, structs, typedefs, enums, locks, callbacks, or host-callable routines.
- The enclosing header, outside this chunk, provides firmware metadata such as `emlxs_lpe11000_label`, kernel/stub/SLI offsets, and eventually the image size/fallback macros consumed by the `emlxs` Fibre Channel adapter driver.
- Firmware-visible entry points are internal branch/call targets encoded directly in the byte stream. They are not symbolized here, but the visible labels identify loop-initialization and frame paths: `RCVD_LIP_F8`, `lipf8_rcvd`, `gxtx_close_timeout`, `IAM_MASTER`, `XMT_ARBF0`, `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `XMT_CLS`, `XMT_LISM`, `RCV_`, and `Sending %s->xcb %x`.

## Control Flow

The chunk continues firmware state dispatch from the prior chunk, then enters FC-AL link/loop event handling. Visible diagnostics cover illegal phase handling, LIP F8 receive, close timeout, loop phase monitoring, OPEN_INIT transitions, and ignored LPB/LPE/LISM cases.

Major visible regions:

- `0x81A88-0x82190`: FC-AL primitive receive/ignore decisions, including `LPB and LPE Rcvd=>ignored`, `ARBF0 in ill phase=%x`, `IAM_MASTER`, `XMT_ARBF0`, `=FL_PORT`, `=lowest`, and `<lowest`.
- `0x82198-0x828F0`: loop initialization primitive handlers for `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, and `XMT_CLS`.
- `0x82900-0x82C78`: AL_PA bitmap/position-map handling with `Master BitMap`, `BitMap[%x]=%08x`, `#of ALPA=%x`, `PosMap=>%02x`, `No Position Map`, and `LINK IS UP!`.
- `0x82CF0-0x832A8`: transmit/sync polling and timeout paths: `Timeout TX Never IDLE`, `Never Sync`, `Never Acquired Sync`, `Sending EOFa`, `FTXQ int never set`, and `SAISR_FTXQ never set`.
- `0x83628-0x838F8`: LIP F7/F8 recovery and loop reinit, including self-vs-peer LIP checks and `LPTOV Timeout`.
- `0x83918-0x84258`: diagnostic frame history and primitive formatting, including transmit/receive names and payload/WWN formatting.
- `0x84678-0x86510`: frame/control-block processing with descriptor field copies and status-byte dispatch.
- `0x86518-0x86E68`: large hardware/firmware initialization sequence with register-like writes, counters, tables, and a `0x11223344` sentinel nearby.
- `0x86F10-0x87A90`: register control, compact branch tables, descriptor setup, and a small constants table.
- `0x87AB8-0x88120`: start of a frame/control-block routine that continues into the next chunk.

## State

The firmware mutates fixed offsets inside structured control blocks. Common visible state includes link/loop fields such as `0x08`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x28`, `0x2c`, `0x30`, `0x38`, `0x3c`, `0x40`, `0x44`, `0x48`, `0x4c`, `0x50`, `0x54`, `0x58`, `0x5a`, `0x60`, `0x64`, `0x68`, `0x6a`, `0x6c`, `0x70`, `0x74`, `0x78`, and `0x7c`.

Byte status/control fields include `0x05`, `0x06`, `0x07`, `0x08`, `0x09`, `0x0a`, `0x0b`, `0x0d`, `0x0f`, `0x10`, `0x11`, `0x21` through `0x27`, `0x32`, `0x39`, `0x3a`, `0x3c`, `0xa0`, `0xa1`, `0xa7`, `0xa9`, `0xac`, `0xad`, `0xd3`, `0xd9`, and `0xdb`.

The visible state machines center on FC-AL loop initialization, LIP F7/F8 recovery, AL_PA map selection, transmit queue readiness, sync acquisition, frame classification, and descriptor/control-block setup.

## Dependencies

- Host build dependency: this byte stream must remain inside `emlxs_lpe11000_image[]` and preserve exact byte order for the `emlxs` firmware loader.
- Firmware runtime dependencies: adapter CPU ISA, firmware memory map, SLI offsets, FC-AL primitive formats, AL_PA maps, mailbox/IOCB/DMA layouts, hardware registers, and shared firmware routines outside this chunk.
- Cross-range dependency: this chunk branches and calls heavily into earlier and later firmware ranges for logging, polling, register access, frame transmission, descriptor allocation, and completion/error handling.
- Driver dependency: illumos `emlxs` treats this as opaque firmware selected and downloaded to the adapter; Solaris kernel code does not execute it directly.

## Risks and Edge Cases

- Any byte edit, truncation, endian conversion, or initializer reordering can corrupt executable adapter firmware.
- Timeout/recovery paths are prominent: `gxtx_close_timeout`, `Timeout TX Never IDLE`, `Never Sync`, `Never Acquired Sync`, `FTXQ int never set`, `SAISR_FTXQ never set`, `LIPF8s > 2 secs`, and `LPTOV Timeout`.
- Loop initialization correctness depends on exact AL_PA bitmap and position-map handling.
- LIP handling distinguishes self-originated and peer-originated primitives; misclassification could cause unnecessary loop resets or missed recovery.
- Several routines scan or copy descriptor regions and use compact branch tables. Bounds and concurrency properties cannot be verified from this header alone.

## Cross-Chunk References

- Previous chunk: contains the state-dispatch routine leading into this span; adjacent prior offsets `0x81900-0x81970` show a branch table and state checks.
- Next chunk: continues the routine cut off at `0x88120`; adjacent following bytes continue field updates through at least `0x88168`.
- Earlier chunks define header metadata and the beginning of `emlxs_lpe11000_image[]`; later chunks complete the image and size/fallback macros.
- The per-file merge should treat this as one opaque LPe11000 firmware image, not as independent C modules.