# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 26561-29878

## Scope

This report covers only the requested range in subset A. The chunk is entirely inside `static uint8_t emlxs_lpe11002_image[]`, the embedded firmware image for the Emulex/Oracle LPe11002-S Fibre Channel adapter. It covers 3,318 byte-array rows, or 26,544 bytes, from firmware offset `0x33D38` through row `0x3A4E0`.

## APIs And Exported Data

This chunk does not introduce host-executed C APIs. There are no C functions, structs, enums, macros, callbacks, locks, allocations, or error paths in the requested line range. Its only C-level contribution is byte data inside the surrounding firmware array.

Adjacent file context provides the host-visible surface: `emlxs_lpe11002_label`, firmware component identifiers, `emlxs_lpe11002_image[]`, and `emlxs_lpe11002_size`. `emlxs_fw.h` binds these into the `LPe11002_FW` `emlxs_firmware_t` table entry.

## Control Flow

There is no source-level C control flow here. At firmware level, the bytes contain ARM-like instruction patterns, literal pools, and embedded diagnostic strings. Visible firmware behavior includes descriptor cleanup, exchange/control-block diagnostics, state classification, table walks, link/adapter state updates, command/ring/buffer paths, DMA reset handling, link-down diagnostics, and loop/old-port synchronization.

Readable firmware strings include `trc dup @%x`, `S/E/XCB %08x`, `Corrupted frame sent %02x`, `Cmd IOCB`, `Wait Buf %x`, `FRxQ Error %08x`, `Reset DMA, no DMA queued`, `Reset DMA, need all DMA queued %d`, `Selected entry stuck - %02x`, `LKDN %08x`, `LD EXP=%08x LPCS=%08x`, `Try_OLDP`, `Try_LOOP`, `Acquire Sync %08x`, `ISSUE LPRQ_INIT`, `TO_LOOP1` through `TO_LOOP6`, `CALLILV3`, `CALLILV4`, `LOSSSYNC`, and `bp init`.

## State And Dependencies

At host C level, this chunk is immutable firmware payload state. The driver consumes it as a contiguous byte image through the firmware table.

Firmware-private state appears to include exchange/control descriptors, IOCB-like command entries, XCB/DCB buffers, free and active queue pointers, response/receive queue counters, link/loop state bytes, DMA reset state, and register snapshots named as PCFG, LPCS, EXP, ELLF, LDBU, and interrupt/endec status.

Build dependencies include `uint8_t`, `EMLXS_FW_IMAGE_DEF`, `MODFW_SUPPORT`, and `emlxs_firmware_t`. Runtime dependencies are the LPe11002/Zephyr adapter CPU, firmware ABI, SLI2/SLI3 expectations, Fibre Channel loop/link protocol behavior, on-card memory layouts, DMA rings, IOCB/XCB/DCB layouts, and adapter registers.

## Risks

The primary risk is binary integrity. A one-byte edit, dropped row, changed order, or mismatch between metadata and bytes can produce a kernel object that compiles while loading broken adapter firmware.

The semantics are opaque to normal C tooling. Source-level analyzers can verify only that this is a byte array; they cannot validate firmware control flow, DMA ordering, register side effects, timeout behavior, or Fibre Channel state-machine correctness.

## Cross-Chunk References

The previous chunk ends at firmware row `0x33D30` and hands directly into this chunk at `0x33D38`; this chunk starts mid-routine. The next chunk starts at `0x3A4E8` and continues the routine entered near `0x3A4B0`.

The final per-file merge should treat this as chunk 9 of 23 for one opaque LPe11002 firmware image and avoid interpreting the byte-array rows as host C APIs.