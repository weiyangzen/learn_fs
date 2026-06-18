# Chunk Research: `fw_lp10000.h` lines 43152-46469

Source slice: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h:43152`

This chunk is a contiguous region of the embedded Emulex LP10000 firmware byte array, `emlxs_lp10000_image[]`, enabled only when `EMLXS_FW_IMAGE_DEF` is defined. There are no C functions, structs, macros, or driver-callable APIs added in this range; the operational semantics are encoded ARM firmware instructions and inline data.

## Firmware Region

- Byte-offset coverage: `0x543B0` through `0x5AB58`.
- Early section contains active firmware code/data with Fibre Channel arbitrated-loop diagnostics.
- Tail becomes a large zero-filled reserved/padding area around `0x5A3xx` through `0x5ABxx`.

## APIs And Dependencies

- No new illumos host-side API is declared.
- Indirect contract: bytes must remain exact because the `emlxs` driver loads this as LP10000 adapter firmware.
- Depends on file-level metadata: `emlxs_lp10000_label`, firmware revision constants, `uint8_t`, 8-byte array alignment, and `EMLXS_FW_IMAGE_DEF`.

## Control Flow Inferred From Strings

Visible firmware diagnostics indicate an arbitrated-loop/link-initialization state machine:

- Primitive receive handling: `LPB and LPE Rcvd=>ignored`, `Rcvd OldPort Prims`, `Ignored(Not a LISM`.
- Port/monitor state: `Unknown port_state=%x`, `Loop Phase=%x`, `Monitor State:Loop_Phase=%x`.
- OPEN init transitions: `To OPEN_INIT Due To:`, `To OPEN_INIT Due To: lipf7_rcvd`.
- Loop primitives: `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `LISM`.
- Transmit states: `XMT_ARBF0`, `XMT_CLS`, `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`.
- Arbitration/AL_PA: `IAM_MASTER`, `=FL_PORT`, `>lowest`, `=lowest`, `<lowest`, `#of ALPA=%x`, `PosMap=>%02x`.
- Recovery/timeouts: `LINK IS UP!`, `Timeout TX Never IDLE`, `Never Sync`, `Never Acquired Sync`, `Issue LipF8s`, `Issue LipF7 Reset to AL_PA=%x`, `LPTO Timeout`.

## State

The firmware appears to manage internal port state, loop phase, monitor state, AL_PA/FL_PORT selection, loop master status, position maps, transmit queue/interrupt state, timeout counters, WWN fields, and primitive payload validation. These are firmware-private encoded offsets, not host-visible C fields.

## Risks

- Opaque firmware: normal C analysis cannot validate memory safety or concurrency.
- Byte order, alignment, padding, and exact offsets are part of the driver/adapter ABI.
- The zero-filled tail may be required for image size/checksum/layout expectations.
- Diagnostic strings help infer behavior but are not a substitute for disassembly.

## Cross-Chunk References

- Previous chunk flows directly into `0x543B0`; adjacent prior context includes `tx_close_timeout`.
- Later chunk/file tail continues zero padding, closes `emlxs_lp10000_image[]`, and defines `emlxs_lp10000_size`.
- File prologue outside this range controls whether the real firmware image or zero firmware macros are exposed.