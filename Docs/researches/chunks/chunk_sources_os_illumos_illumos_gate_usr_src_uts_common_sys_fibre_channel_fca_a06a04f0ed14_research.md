# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 39833-43150

## Scope

This report covers only `fw_lpe11000.h` lines 39833-43150 in learn_fs subset A. The chunk is a middle slice of the Emulex LPe11000 firmware byte array, spanning firmware image offsets `0x4DBF8` through `0x543A7` inside `static uint8_t emlxs_lpe11000_image[]`.

## APIs And Exported Data

This chunk exports no standalone C APIs, structs, macros, or callable illumos functions. Its only contribution is contiguous initializer data for `emlxs_lpe11000_image[]`.

Host-side publication is through adjacent context: `emlxs_fw.h` maps `LPe11000_FW` to this image and metadata, and `emlxs_adapters.h` associates it with Zephyr LPe11000 and Oracle LPe11000-S adapter records.

## Control Flow

There is no host C control flow here. The byte stream is ARM firmware code plus embedded literal/string data. Visible firmware control flow includes function prologues/epilogues, subroutine calls, conditional branches, jump-table-like branch runs, and PC-relative literal loads.

Visible logic appears to cover FC command, IOCB, XRI/RPI, ring/list-buffer, abort, timeout, queue, and DMA reset handling. Embedded diagnostics include `T/O x %x %x`, `ABTS XRI/RPI %08x (%x)`, `No find %x(%x)`, `Cmd IOCB`, `Wait Buf %x`, `Need XRI/Ring ListBuf`, `Toss %x`, DMA reset messages, and `Selected entry stuck - %02x`.

## State And Dependencies

The C-visible state is immutable firmware image data emitted when `EMLXS_FW_IMAGE_DEF` is enabled. Firmware-visible state is hard-coded through structure offsets and literal addresses. Frequently visible offsets include `0x06`, `0x07`, `0x08`, `0x0a`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x28`, `0x2c`, `0x30`, `0x3c`, `0x4c`, `0x50`, `0x5c`, `0x64`, `0x6c`, `0x70`, `0x7c`, `0x80`, `0xac`, and `0xb8`, plus larger offsets such as `0x260`, `0x264`, `0x270`, `0x2d8`, `0x2f8`, `0x700`, and `0x70c`.

## Risks And Cross-Chunk References

The main risk is byte-level fragility: any corruption, omitted comma, or reordered initializer entry can change device-executed firmware while remaining syntactically valid C.

This chunk starts mid-routine at `0x4DBF8` and ends mid-routine at `0x543A0`. Previous chunks contain the image header, entry vectors, and earlier firmware routines called here; the next chunk continues branch/call targets and DMA/queue-selection logic.