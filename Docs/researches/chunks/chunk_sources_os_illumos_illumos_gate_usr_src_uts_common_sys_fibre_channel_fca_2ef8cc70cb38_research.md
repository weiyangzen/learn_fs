# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h lines 19926-23243

## Scope

This report covers only chunk 7 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h`, lines 19926-23243, in learn_fs subset A (`Docs/research_subset_a.md`). I read the full requested line range and used adjacent context only to identify the enclosing header/image declaration and the chunk boundaries. This chunk is an interior segment of the embedded Emulex LP10000 firmware image, not ordinary host-side driver C logic.

## APIs And Exported Data

No new C functions, macros, structures, or host-callable APIs are declared in this line range. The only host-visible object is the already-open `static uint8_t emlxs_lp10000_image[]` initializer, emitted only under `EMLXS_FW_IMAGE_DEF`.

Adjacent header context identifies the wrapper API for the whole file: `emlxs_lp10000_label`, firmware entry/version offset macros, 8-byte image alignment, and final image size `0x5BD00` outside this chunk.

Inside the blob, visible data includes ARM instruction words, literal address pools, dispatch/jump tables, diagnostic strings, register/status masks, queue pointers, and sentinel words such as `0x98765432`.

## Control Flow

At the C level, there is no executable control flow in this chunk. It is byte initializer data.

At the firmware level, the chunk begins at offset `0x26DE0` and contains many ARM routine boundaries, conditional branches, backwards polling loops, and calls/branches into earlier and later firmware offsets.

Notable visible behavior includes low-level setup/status routines, queue/list structure updates, command/event dispatch tables, IOCB/exchange handling, ABTS diagnostics, response-ring handling, frame validation, duplicate/trace handling, DMA reset paths, and multi-channel state selection. Visible diagnostics include `wait %x`, `Starve abt`, `ABTS XRI/RPI`, `Blkd RSP Ring`, `No find`, `trc dup`, `S/E/XCB`, `Corrupted frame sent`, `Cmd IOCB`, `Wait Buf %x`, `Toss %x`, `FRxQ Error`, `BIUE`, and DMA reset messages.

## State And Dependencies

The host-visible state is immutable firmware bytes compiled into the driver image. The chunk depends on the surrounding declaration of `emlxs_lp10000_image[]`, `uint8_t`, `EMLXS_FW_IMAGE_DEF`, and header guards.

Firmware-internal state is opaque but visibly centered on memory-mapped hardware/register regions, work queues/rings, IOCB-like structures, diagnostic/logging routines, and literal-pool addresses in the `0x0002xxxx` and `0x0003xxxx` ranges. Frequently referenced offsets include `0x20`, `0x24`, `0x30`, `0x64`, `0x66`, `0xAF`, `0x100`, `0x260`, `0x38C`, `0x390`, `0x394`, `0x398`, `0x39C`, `0x3A0`, and `0x70C`.

## Risks

The main risk is binary integrity. This chunk is executable firmware encoded as C initializer bytes; any byte-level edit can silently change hardware initialization, queue handling, DMA reset behavior, diagnostic paths, or branch targets while still compiling.

Semantic review is limited without firmware source or disassembly labels. The visible diagnostics and offsets strongly suggest Fibre Channel adapter queue, frame, ABTS, IOCB, DMA, and link/control handling, but exact invariants are firmware-private.

The host build contract is also sensitive: `EMLXS_FW_IMAGE_DEF` must be defined only in the intended owning translation unit so the real image is emitted once.

## Cross-Chunk References

This chunk starts at firmware offset `0x26DE0` after a routine in the previous chunk; adjacent lines 19880-19925 show prior status copying and branching setup.

This chunk ends mid-routine at firmware offset `0x2D588`. The next chunk continues multi-channel status/selection logic around fields `0x394`, `0x398`, `0x39C`, `0x3A0`, `0x70C`, and `0x38C`.

Many branch and literal-pool targets point outside this chunk, both earlier and later in the image. The final per-file report must merge this with neighboring chunks to describe the full LP10000 firmware image wrapper, trailer, and exact final size handling.