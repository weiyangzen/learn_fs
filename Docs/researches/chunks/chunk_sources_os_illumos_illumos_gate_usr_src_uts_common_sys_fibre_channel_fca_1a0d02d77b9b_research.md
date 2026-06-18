# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 59742-63059

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: generated/embedded Emulex LP11002 firmware image header, not normal host-side C implementation.
- This chunk is inside `static uint8_t emlxs_lp11002_image[]`, defined only when `EMLXS_FW_IMAGE_DEF` is set.
- Firmware identity from file context: `LP11002-S: v2.82a4 (bf282a4.all)`.
- File-level image size from the footer: `sizeof (emlxs_lp11002_image)`, with array comment showing `0x8DCB8` bytes.
- Chunk coverage: firmware offsets `0x74A20` through `0x7B1CF`. The chunk starts inside firmware control flow and ends mid-routine; the next source line continues at `0x7B1D0`.

## APIs And Host Surface

- No C functions, typedefs, structs, or host-callable APIs are declared in this range.
- The only host-visible object represented by this range is the enclosing opaque firmware byte array `emlxs_lp11002_image[]`.
- Outside this chunk, `emlxs_fw.h` includes `fw_lp11002.h` and registers `LP11002_FW` with `emlxs_lp11002_size`, image pointer, label, and SLI version constants.
- Outside this chunk, `emlxs_adapters.h` maps supported LP11002 adapter entries to `LP11002_FW`.

## Control Flow

- Bytes are ARM-style firmware instructions mixed with literal pools and diagnostic strings. They should be read as controller firmware, not as C statements.
- The opening routine at `0x74A20` clears and sets fields around object offsets such as `0x00`, `0x08`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, and `0xa4`, then emits or references the diagnostic `Corrupted frame sent %02x`.
- Around `0x74B88`-`0x74D00`, a copy/queue routine polls status fields around `0x94`, `0x9c`, and `0xab`, copies records in `0x1c`-byte units, and updates queue-like pointers/counters.
- Around `0x74E40`-`0x75010`, a dispatch path branches through many case targets based on a byte near offset `0x07`, updates command/entry fields, and references `Cmd IOCB`.
- Around `0x75E00`-`0x76300`, repeated bit tests drive hardware/register writes using constants near `0x296` and `0x2a6`.
- Around `0x76670`-`0x76DC0`, error/status handling updates aggregate masks, counters, and queue state; diagnostics include `BIUE: %08x`, `Reset DMA`, and `Selected entry stuck - %02x`.
- Later paths expose link/loop, abort/reject, and old-port transitions through strings including `LKDN`, `LDBU`, `BARJT`, `BAACC buf`, `ABTSbuf`, `RJT buf`, `Try_OLDP`, `Try_LOOP`, `Acquire Sync`, `ISSUE LPRQ_INIT`, `LOOP ACTIVE!!!`, `CALLILV3`, `LOSS SYNC`, and `TO_LOOP1` through `TO_LOOP6`.
- Near `0x7AFE8`, `bp init` marks a boot/bring-up or buffer-pool initialization path. The chunk ends at `0x7B1C8` inside a new routine that continues in the next chunk.

## State, Dependencies, And Risks

- Active object fields include `0x06`, `0x07`, `0x08`, `0x0c`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x30`, `0x34`, `0x39`, `0x40`, `0x4c`, `0x50`, `0x60`, `0x6c`, `0x80`-`0x84`, `0x94`, `0x98`, `0x9c`, `0xa0`, `0xa4`, `0xab`, `0xac`, `0xb8`, `0xd3`, and `0xdb`.
- Larger firmware/global offsets include `0x290`, `0x304`, `0x370`, `0x4f0`, `0x500`-`0x50c`, `0x638`, `0x658`, `0x660`, `0x700`-`0x708`, `0x800`, `0x804`, `0x818`, and counters around `0x1d4`-`0x1f4`.
- Runtime dependencies are the LP11002 adapter CPU, firmware memory map, hardware registers, SLI2/SLI3 behavior, and Fibre Channel protocol state machine.
- Any byte-level edit can break instruction encoding, branch targets, literal addresses, diagnostics, firmware integrity, or driver-version coupling.

## Cross-Chunk References

- Previous chunk: this range starts at `0x74A20`, immediately after control-flow and field-update logic at `0x74A10`-`0x74A18`.
- Next chunk: the routine beginning near `0x7B1A8` continues at `0x7B1D0`, with fields around `0x6c`, `0x38`, `0x40`, `0x70`, and counters at `0x1e4`-`0x1f0`.
- File-level merge should keep this separate from similar `fw_lpe11002.h` chunks; this file is `fw_lp11002.h` and has LP-specific label, constants, and image size.