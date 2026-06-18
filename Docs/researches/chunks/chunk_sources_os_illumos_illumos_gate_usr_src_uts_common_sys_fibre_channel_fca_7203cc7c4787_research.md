# Chunk Research: `fw_lp11002.h` Lines 33198-36515

This chunk is not normal C implementation logic. It is a contiguous slice of the `emlxs_lp11002_image[]` firmware byte array for the Emulex LP11002 Fibre Channel adapter, covering image offsets `0x40CA0` through `0x47448`. The host-visible API remains the surrounding header contract: LP11002 version/address macros plus the conditional `static uint8_t emlxs_lp11002_image[]` definition under `EMLXS_FW_IMAGE_DEF`. Inside this chunk there are no C functions, structs, enums, or callable host-side symbols.

The visible firmware content is ARM-style instruction bytes mixed with literal pools, register/register-region tables, sparse zero-filled data, and embedded diagnostic/format strings. It appears to cover adapter-side initialization, register-table publication/copying, low-level memory/register access helpers, and later Fibre Channel receive/exchange buffer handling.

Key visible behaviors:

- Starts mid-routine around `0x40CA0`, already executing branch/call-heavy firmware code from the previous chunk.
- Early routines manipulate apparent control/status fields such as `+0x0C`, `+0x30`, `+0x40`, `+0x48`, `+0x4C`, `+0x50`, `+0x358`, and `+0x4F0`.
- Around `0x410D8`-`0x415F0`, exposes structured hardware/register-region tables with labels `LINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, and `DEND`.
- The table is followed by code that appears to copy descriptors, issue low-level operations, and toggle control bits in `0x0A...` and `0x0B...` register spaces.
- Embedded diagnostics near `0x46250` include `TIME: %08x  %s`, `%08x:`, `%08x %08x`, and `Rcverr Frm %x. Idx %x.`.
- The later region from roughly `0x46A00` onward updates per-object fields including `+0x61`-`+0x63`, `+0x68`-`+0x6E`, `+0x70`-`+0x7A`, `+0x260`, `+0x270`, `+0x2F8`, `+0x340`, `+0x348`, `+0x350`, and `+0x378`.
- The tail contains queue/exchange-like copy and update logic, with length/count checks around `0x08`, `0x0C`, `0x24`, and `0x3C`.

State and data model:

- C-level state is only bytes in `emlxs_lp11002_image[]`.
- Firmware-side state appears to include adapter global state, register-region descriptors, queue state, receive-frame state, counters, flags, and per-exchange/buffer descriptors.
- The visible table labels identify link, BIU, control RAM, receive queue, FIFO, RDMA, TDMA, and related hardware blocks.

Dependencies:

- Host-side illumos code depends on this chunk as opaque firmware data.
- Runtime dependencies are the LP11002 adapter CPU, firmware instruction set, adapter memory map, SLI/Fibre Channel conventions, and exact register layout.
- Byte order, alignment, offsets, and size must be preserved.
- Firmware routines branch to helpers outside this line range in both directions.

Risks:

- Any byte-level edit can corrupt instructions, literal pools, branch targets, register tables, or diagnostics.
- Normal C tooling cannot validate the firmware semantics.
- The register-table block is offset-sensitive.
- Visible polling/register-toggle paths could hang initialization, link recovery, or receive handling if surrounding state is wrong.
- Receive/error processing near the tail is only partially visible.

Cross-chunk references:

- The first line (`0x40CA0`) continues executable flow from the previous chunk.
- The register/data table section is likely consumed by code immediately before and after it.
- The final line (`0x47448`) ends mid-routine; control flow continues into the next chunk.