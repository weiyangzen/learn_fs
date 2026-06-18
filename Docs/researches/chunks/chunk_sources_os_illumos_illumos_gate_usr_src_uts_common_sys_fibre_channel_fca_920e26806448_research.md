# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h lines 49787-53104

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h` lines 49787-53104 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, neighboring chunk boundaries, and host firmware-table integration.

The chunk is a contiguous slice of the generated `static uint8_t emlxs_lpe12000_image[]` firmware byte initializer for the Emulex LPe12000 Fibre Channel adapter. It is not ordinary host-executed C source.

## APIs And Exported Data

This chunk exports no C functions, structs, macros, callbacks, or host-callable APIs. Its only C-visible contribution is 26,544 bytes added to the private firmware image symbol `emlxs_lpe12000_image[]`, which is emitted only when `EMLXS_FW_IMAGE_DEF` is defined.

The surrounding header metadata identifies the full image as `LPe12000-S: v2.01a4 (ud201a4.all)` and defines image constants such as `emlxs_lpe12000_kern`, `emlxs_lpe12000_stub`, `emlxs_lpe12000_sli2`, and `emlxs_lpe12000_sli3`. Adjacent integration in `emlxs_fw.h` places the image pointer, image size, label, and revision markers into the `LPe12000_FW` entry of `EMLXS_FW_TABLE`.

Firmware offsets covered by this chunk run from row `0x61308` through row `0x67AB0`, ending at byte `0x67AB7`. The byte interval is `[0x61308, 0x67AB8)`.

## Control Flow

There is no illumos kernel control flow in this range. The C compiler only compiles array initializers.

The byte stream itself has ARM-like firmware instruction structure: register-save prologues (`E9 2D`), returns/restores (`E8 BD` / `E1 A0 F0 0E`), branches (`EA`), branch-with-link calls (`EB`), loads/stores (`E5`), and immediate/mask operations (`E3`). Visible routines manipulate pointer-relative state, loop over queue/list entries, increment counters, and branch into shared firmware helpers outside this chunk.

The readable embedded diagnostic strings in this interval point to firmware paths for DMA/link handling, loop/link synchronization, exchange start failure, abort processing, buffer release, and timeout/error reporting. Examples include `DWNLW %08x`, `LD EXP=%08x LPCS=%08x`, `irqEndecIntL PCFG=%x`, `BARJT %x`, `BAACC buf %x`, `ABTSbuf %x`, `XCB 0: Can't start xchg`, `WRI %x deadx %4x`, `OOOFrm`, `Acquire Sync %08x`, `ISSUE LPRQ_INIT`, `LOOP ACTIVE!!!`, `4 sec t.o.`, `LOSSSYNC`, `Rls free buf %x`, `dup get`, `Abt Req %x%04x`, `Fnd abt x %x`, and `Abt Mtpl %08x`.

## State And Dependencies

From the host driver's perspective, this chunk has no mutable C state, allocation, locks, or direct kernel object dependencies. It only supplies immutable bytes inside the full firmware image.

Within the firmware bytes, recurring state offsets suggest device-side structures for queues, exchange/control blocks, link state, status bytes, and counters. Common offsets visible in loads/stores include low structure fields such as `0x04`, `0x06`, `0x07`, `0x08`, `0x0C`, `0x10`, `0x18`, `0x1C`, `0x20`, `0x26`, `0x27`, `0x28`, `0x2C`, `0x30`, `0x34`, `0x38`, `0x3C`, `0x40`-`0x44`, `0x4C`, `0x50`, `0x54`, `0x58`, `0x6C`, `0x72`, `0x80`, `0x8C`, `0xA7`-`0xB1`, and larger firmware-private offsets such as `0x180`, `0x198`, `0x1A0`, `0x1A8`, `0x1B0`, `0x210`, `0x234`, `0x244`, `0x248`, `0x2C0`-`0x2DC`, `0x2F8`, `0x304`, `0x340`, `0x350`, and `0x638`.

Compile-time dependencies are inherited from the enclosing header: `uint8_t`, `_FW_LPE12000_H`, `EMLXS_FW_IMAGE_DEF`, and `#pragma align 8(emlxs_lpe12000_image)`. Runtime dependencies are indirect and device-specific: the emlxs driver downloads this opaque image to LPe12000 adapter firmware execution hardware using the broader firmware-loading path.

## Risks And Cross-Chunk References

A one-byte edit in this chunk can silently change adapter firmware instructions, literal pools, strings, branch targets, queue handling, link recovery, or abort/error paths while leaving the C build syntactically valid. Because this data is opaque to normal C analysis, integrity/version mismatches and accidental regeneration drift are the main maintenance risks.

This chunk starts immediately after chunk 15 at firmware offset `0x61308` and continues into chunk 17 at `0x67AB8`; both boundaries are inside `emlxs_lpe12000_image[]` and may split firmware routines. Earlier chunks define the image header and preceding code/data. Later chunks continue the same initializer through additional firmware routines, literal data, and the closing image-size definition. The final per-file report should merge chunk findings as an opaque firmware image rather than treating this range as standalone C logic.