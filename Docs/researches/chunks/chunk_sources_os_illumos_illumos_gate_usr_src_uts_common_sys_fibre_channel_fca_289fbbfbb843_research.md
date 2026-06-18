# Chunk Research: fw_lp10000.h lines 39834-43151

Source scope: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h`, chunk 13, lines 39834-43151. This range is entirely inside `static uint8_t emlxs_lp10000_image[]`, the embedded Emulex LP10000 firmware image. The exact firmware byte offsets covered are `0x4DC00` through `0x543AF`.

## APIs and Entry Surface

This chunk does not define C APIs, structs, macros, or callable driver functions. Its only source-level role is as byte data included in `emlxs_lp10000_image[]` when `EMLXS_FW_IMAGE_DEF` is enabled. The host driver consumes the complete array through the LP10000 firmware table in `emlxs_fw.h`.

The executable surface visible here is firmware-internal, not illumos kernel C. The bytes are ARM-like instructions, branch/call words, literal pointers, and embedded diagnostic strings.

## Control Flow Observations

The chunk begins mid-routine. Lines 39834-39836 loop around a previous call/result check and return zero on completion; preceding chunk lines set this up.

Several firmware routine prologues/returns are visible around offsets `0x4DC18`, `0x4E000`, `0x4E090`, `0x4E200`, `0x4E250`, `0x4E2C0`, `0x540D8`, `0x541B8`, and `0x542A0`.

Visible embedded strings anchor behavior around link, loop, exchange, abort, and timeout handling, including `LKDN %08x`, `LD EXP=%08x LPCS=%08x`, `@XMT XRI mismatch`, `ABTSbuf`, `Begin RRQ`, `State %02x->%x`, `Ill phase`, `RCVD_LIP_F8`, `lipf8_rcvd`, and `tx_close_timeout`.

Offsets `0x540D8`-`0x541B8` implement a phase dispatcher with a branch table and an invalid-phase path. Offsets `0x541B8`-`0x54298` handle received LIP F8. Offsets `0x542A0`-`0x543AF` begin a transmit-close timeout path and continue into the next chunk.

## State and Data

State is firmware-local and represented by numeric offsets into firmware control blocks or memory-mapped regions. Repeated offsets include `0x14`, `0x18`, `0x28`, `0x2C`, `0x30`, `0x4C`, `0x4D`, `0x50`, `0x5B`, `0x5C`, `0x79`, `0x9C`, `0xD3`, `0xD8`, `0xDB`, `0x174`, `0x17C`, `0x184`, `0x1A4`, `0x1B4`, `0x270`, and `0x37C`.

Visible control concepts include link down, expected link events, loop active, old-port discovery, LIP F8 reception, transmit close timeout, abort request, RRQ, XRI/XID/RPI/SID handling, and buffer allocation/freeing.

## Dependencies

Compile-time dependency: this chunk depends on the containing header context that declares `emlxs_lp10000_image[]`.

Driver dependency: `emlxs_fw.h` includes `fw_lp10000.h` and places this image in `EMLXS_FW_TABLE` for `LP10000_FW`.

Runtime dependency: the firmware bytes depend on LP10000 adapter hardware registers, firmware-resident tables, mailbox/exchange-control memory layouts, and link-state machinery not defined in this chunk.

## Risks and Maintenance Notes

Manual edits to any byte in this chunk can silently alter adapter firmware behavior. Corruption would likely appear as firmware load failure, link negotiation failure, exchange abort mishandling, or Fibre Channel transport errors.

Embedded strings are useful evidence of nearby behavior, but strings and executable bytes are interleaved. They should not be treated as exact function boundaries.

The chunk begins and ends mid-control-flow. The opening continuation must be joined with chunk 12, and the unfinished `tx_close_timeout`/LPB-LPE handling must be joined with chunk 14.

## Cross-Chunk References

Previous chunk: offsets `0x4DB90`-`0x4DBF8` set up helper calls and branch into this chunk.

Next chunk: line 43152, offset `0x543B0`, starts `LPB and LPE Rcvd=>ignored`, continuing the timeout/event handling begun here.

Host-side: `emlxs_fw.h` maps the complete `emlxs_lp10000_image[]` into the LP10000 firmware table, so this chunk is one internal region of a firmware image rather than an independent illumos driver module.