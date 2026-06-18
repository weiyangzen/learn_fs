# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 69695-70884

## Scope

This report covers only chunk 22 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h`, lines 69695-70884, in learn_fs subset A (`Docs/research_subset_a.md`). I read the full requested line range and used adjacent context only to identify the enclosing `emlxs_lpe11000_image` declaration and conditional footer. This chunk is the tail of an embedded Emulex LPe11000 firmware image, not normal driver C logic.

## APIs And Exported Data

The only C-level API surface completed in this chunk is the firmware image wrapper:

- Lines 69695-70867 continue and finish `static uint8_t emlxs_lpe11000_image[]`, whose enclosing declaration is under `#ifdef EMLXS_FW_IMAGE_DEF`.
- Line 70869 closes the initializer and records the firmware payload length as `0x8A5CC` bytes.
- Line 70871 defines `emlxs_lpe11000_size` as `sizeof (emlxs_lpe11000_image)` when the image is compiled in.
- Lines 70873-70878 provide the no-image fallback: `emlxs_lpe11000_image` and `emlxs_lpe11000_size` both expand to `0`.
- Lines 70880-70884 close the C++ extern block and `_FW_LPE11000_H` include guard.

Within the blob, visible data includes firmware-internal code/data rather than C symbols. The chunk contains ARM instruction words, literal addresses, register/block descriptor tables, masks, constants, padding, and final signature-like words.

## Control Flow

At the firmware level, lines 69695-70397 are mostly ARM code mixed with literal pools. The byte patterns show routine boundaries, conditional branches, loops, subroutine calls, table branches, and returns through `LR`. Several branches/calls target firmware offsets outside this chunk, so the full firmware control graph is cross-chunk.

Notable visible behavior:

- The chunk starts mid-routine at firmware offset `0x88128`; entry state is in the previous chunk.
- Repeated state-machine style handlers inspect and update small status fields at offsets such as `0x0c`, `0x11`, `0x13`, `0x1c`, `0x20`, `0x28`, `0x3c`, `0x58`, and `0x5f`.
- Several routines manipulate linked/list-like pointers and queue heads.
- Lines 70283-70285 include the diagnostic string `Rcverr Frm %x. Idx %x.\n`.
- Lines 70298-70458 contain named firmware data tables: `LINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, `PCIR`, and `DEND`.
- Lines 70461-70532 resume low-level ARM code with software interrupts, processor/control-register style opcodes, and branches to earlier firmware addresses.
- Lines 70533-70637 are primarily address/vector tables pointing to firmware offsets in the `0x07xxxx`, `0x08xxxx`, and `0x09xxxx` ranges.
- Lines 70638-70867 are mostly zero-filled or sparse configuration/trailer data, including `0x12345678`, `0xffffffff`, `0x2710`, `0x0fa0`, `0x0800`, `0x0100`, `0x1000`, `0x2000`, `0x01ff`, and final repeated `0x55` bytes.

At the host C level, there is no executable control flow besides preprocessor selection between an embedded image and a disabled-image stub.

## State And Dependencies

The host-visible state is immutable compiled data. When `EMLXS_FW_IMAGE_DEF` is defined in exactly one translation unit, this header emits the static byte array and its size macro. Without that macro, consumers see `emlxs_lpe11000_image == 0` and `emlxs_lpe11000_size == 0`.

Direct C dependencies visible from adjacent context are `uint8_t`, `#pragma align 8(emlxs_lpe11000_image)`, `EMLXS_FW_IMAGE_DEF`, `_FW_LPE11000_H`, and optional C++ linkage guards. Earlier header metadata names this payload `LPe11000-S: v2.82a4 (zd282a4.all)` and defines firmware offsets for `kern`, `stub`, and SLI variants.

Firmware-internal dependencies are opaque hardware/ASIC contracts: memory-mapped register layouts, queue formats, block IDs, and firmware absolute addresses. The visible block labels suggest internal register dump or initialization descriptors for link, bus/interface, RAM, receive queues, FIFO, DMA, and PCI-related units.

## Risks

The main risk is blob integrity. A one-byte edit can change firmware execution, table targets, hardware register programming, diagnostics, or final validation/trailer data while still compiling cleanly. The C compiler cannot validate the firmware semantics.

The `EMLXS_FW_IMAGE_DEF` split is build-sensitive: defining it in multiple translation units would duplicate a large static image, while failing to define it in the intended image-owning translation unit leaves only the `0` fallback macros.

The closing size comment and `sizeof` definition must remain synchronized with the initializer. Tools or driver code that expect the exact `0x8A5CC` byte image may reject or misload a changed payload.

## Cross-Chunk References

This chunk begins in the middle of firmware code; chunk 21 contains the preceding bytes and entry context for the routine at offset `0x88128`. Many visible branches and literal addresses target earlier firmware offsets, so semantic reconstruction requires previous chunks.

This is the final chunk for `fw_lpe11000.h`: it closes `emlxs_lpe11000_image`, defines the image size/fallback macros, and closes all header guards. There is no next chunk for this file, but the final per-file report must merge this footer/trailer information with earlier chunks.