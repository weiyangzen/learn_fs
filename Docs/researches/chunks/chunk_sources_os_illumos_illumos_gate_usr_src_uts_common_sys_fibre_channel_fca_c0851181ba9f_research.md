# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 26562-29879

## Scope

This chunk is a contiguous interior slice of the `emlxs_lp11000_image[]` firmware byte initializer for the Emulex LP11000 Fibre Channel adapter firmware in illumos `emlxs`. It is in subset A through `sources/os/illumos/illumos-gate` as defined by `Docs/research_subset_a.md`.

The covered source lines are pure byte literals, not host-executed C. The image offsets covered are `0x33D40` through `0x3A4EF`, for 26,544 bytes. The next chunk begins at `0x3A4F0`.

## APIs And Entry Points

No C functions, structs, macros, or illumos driver entry points are declared in this line range. The host-visible surface is inherited from the surrounding header:

- `emlxs_lp11000_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- `emlxs_lp11000_size`, defined outside this chunk from the full image size.
- File-level metadata such as `emlxs_lp11000_label` (`LP11000-S: v2.82a4 (bd282a4.all)`) and the `emlxs_lp11000_kern/stub/sli*` constants.

Firmware-internal routines are visible only as ARM-like instruction bytes, branch targets, literal pools, and embedded diagnostic strings. Prologue/epilogue patterns mark probable on-adapter routine boundaries, but the C source has no symbols or signatures for them.

## Control Flow And Behavior

This chunk starts in the middle of queue/entry cleanup logic continued from the prior chunk, then enters a larger firmware state machine.

Visible diagnostic strings identify link acquisition and loop handling (`Try_OLDP`, `Try_LOOP`, `Acquire Sync %08x`, `ISSUE LPRQ_INIT`), loop-active and timeout transitions (`LOSSSYNC`, `TO_LOOP*`, `TO_OLDP*`), buffer/exchange recovery (`bad buffer rls`, `Begin RRQ %x->rpi %02x`, `killing xchg due to continue`), LIP handling (`RCVD_LIP_F8`, `lipf8_rcvd`, `xtx_close_timeout`), and loop initialization primitive transmit paths (`XMT_ARBF0`, `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`).

The chunk also exposes ALPA/position-map and link-up reporting (`Master BitMap`, `BitMap[%x]=%08x`, `#of ALPA=%x`, `PosMap=>%02x`, `LINK IS UP!`) plus link incident timing/reset behavior (`Never Sync`, `Never Acquired Sync`, `Issue LipF7 Reset to AL_PA=%x`, `LPTOV Timeout`, `ILV=>REINIT=%x`).

## State

The firmware manipulates adapter-private data structures by fixed offsets from register-held base pointers. Recurring low object/control fields include `+0x04`, `+0x06` through `+0x14`, `+0x18`, `+0x1C`, `+0x20`, `+0x24`, `+0x28`, `+0x2C`, `+0x30`, `+0x3C`, `+0x40`, `+0x48`, `+0x4A` through `+0x53`, `+0x58`, `+0x5C`, `+0x60`, `+0x68`, `+0x69`, `+0x6C`, `+0x70`, `+0x72`, `+0x73`, `+0x74`, and `+0x79`.

Larger internal/global offsets include `+0x90`, `+0x94`, `+0x9C`, `+0xA0`, `+0xA8`, `+0xAA`, `+0xB0`, `+0xB9`, `+0xD3`, `+0xDB`, `+0x128`, `+0x134`, `+0x13C`, `+0x140`, `+0x144`, `+0x148`, `+0x150`, `+0x158`, `+0x15C`, `+0x160`, `+0x164`, `+0x170`, `+0x180`, `+0x188`, `+0x190`, `+0x194`, `+0x260`, `+0x374`, and `+0x37C`.

The strings show tracking of loop initialization state, old-port recovery, local SID/AL_PA identity, WWN/payload comparisons, receive/transmit primitive classification, exchange abort/recovery, RRQ handling, buffer release/freeing, timeout counters, and reinitialization triggers.

## Dependencies

- Build-time dependency: the bytes are meaningful only as part of the enclosing `fw_lp11000.h` firmware image and only become a real array when `EMLXS_FW_IMAGE_DEF` is defined.
- Driver dependency: `emlxs_fw.h` consumes the whole LP11000 image and metadata through the firmware table; this chunk is not independently addressable by host code.
- Hardware dependency: the payload depends on the LP11000 adapter CPU, firmware memory map, SLI/Fibre Channel link semantics, loop initialization primitives, adapter registers, DMA/queue state, and on-card control-block layout.
- Firmware-internal dependency: branch/call opcodes target helper routines and data outside this chunk, including logging/formatting routines, queue helpers, link-state helpers, and handlers continued in neighboring chunks.

## Risks And Maintenance Notes

Treat this range as immutable generated/vendor firmware. Any byte edit can corrupt ARM instructions, literal pools, PC-relative branches, string references, alignment, checksums, or hardware-visible state.

Link/loop code is state-machine sensitive. Corruption in this chunk could cause link acquisition failure, endless LIP/reset cycles, bad ALPA/position-map handling, fabric/loop login failure, stuck exchanges, or adapter firmware hangs.

Buffer, RRQ, abort, and exchange cleanup paths appear interleaved with link-state logic. A wrong field offset or branch target could leak/free the wrong firmware buffer or kill an active exchange.

## Cross-Chunk References

- Previous chunk: lines 23244-26561 end in queue/entry cleanup and out-of-order frame handling. This chunk starts at `0x33D40` in the middle of that control flow.
- Next chunk: lines 29880-33197 start at `0x3A4F0` and continue the routine that begins near the end of this chunk, including later `LIPF7` and `RCV_MyLIPF8 : DID=%08x` paths.
- File-level context: chunk 1 defines the header guard, LP11000 metadata macros, and starts `emlxs_lp11000_image[]`; the final chunk closes the array and defines `emlxs_lp11000_size` / fallback zero macros.
- Per-file merge note: this report should be merged as one byte-range slice of the single LP11000 firmware image, not as an independent source module or C implementation unit.