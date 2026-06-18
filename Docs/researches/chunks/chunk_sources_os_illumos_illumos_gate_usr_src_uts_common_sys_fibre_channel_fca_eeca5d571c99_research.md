# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 73013-73375

Scope: learn_fs subset A includes `sources/os/illumos/illumos-gate`. This report covers only ordered chunk 23, the final span of `fw_lpe11002.h`. I read lines 73013-73375 completely and used adjacent context only to identify the enclosing firmware image declaration and table consumer.

This chunk is the tail of the generated Emulex LPe11002-S firmware header. Lines 73013-73358 are the final bytes of `static uint8_t emlxs_lpe11002_image[]`, spanning firmware offsets `0x8E8D8` through `0x8F3A7`. Lines 73360-73375 close the array, define the size macro, define the no-embedded-image fallback macros, and close the `EMLXS_FW_IMAGE_DEF`, C++, and header-guard conditionals.

## Host-visible API surface

- `emlxs_lpe11002_image[]`: completes the 8-byte-aligned firmware byte array emitted when `EMLXS_FW_IMAGE_DEF` is defined.
- `emlxs_lpe11002_size`: defined here as `sizeof (emlxs_lpe11002_image)` after the array close.
- Fallback macros: when `EMLXS_FW_IMAGE_DEF` is not defined, this chunk defines `emlxs_lpe11002_image` as `0` and `emlxs_lpe11002_size` as `0`.
- Closure of wrapper conditionals: `#endif /* EMLXS_FW_IMAGE_DEF */`, C++ `extern "C"` close, and `#endif /* _FW_LPE11002_H */`.

No C functions, structs, typedefs, enums, locks, callbacks, or host-callable driver routines are implemented in this chunk. The driver-facing contract is data plus macros. `emlxs_fw.h` consumes these symbols in the `LPe11002_FW` table entry with `emlxs_lpe11002_label`, `kern`, `stub`, and SLI revision constants defined earlier in this header.

## Control flow

At host C level, control flow is entirely preprocessor-controlled:

- If the including translation unit defines `EMLXS_FW_IMAGE_DEF`, lines 73013-73362 contribute the final firmware bytes and expose `emlxs_lpe11002_size` as the actual image length.
- If not, lines 73364-73367 skip the image and expose zero-valued image/size macros.
- `emlxs_fw.h` defines `EMLXS_FW_IMAGE_DEF` while building the firmware table unless `MODFW_SUPPORT` is enabled, so modular/external firmware builds intentionally take the zero-image path.

Within the opaque firmware payload, the first few rows continue ARM-like instruction words from the previous chunk, including stack/register restore patterns and branches. Around offset `0x8E920`, the payload changes into address tables, byte lookup maps, sparse configuration/value blocks, zero padding, sentinel patterns such as `0x12345678`, and final trailer/checksum-like bytes at `0x8F398-0x8F3A7`. The host compiler does not interpret this firmware-side control flow.

## State and data layout

- Final image size is declared in-line as `0x8F3A8` bytes at the array close.
- The chunk starts at firmware offset `0x8E8D8` and ends at `0x8F3A7`, contributing the final `0xAD0` bytes of the image.
- Rows `0x8E920-0x8E95F` contain repeated firmware addresses, notably `0x0005D024` and several `0x00073xxx/0x000740xx/0x000743xx` targets.
- Rows `0x8E960-0x8EA63` form a dense byte lookup table with many `0x80` placeholder/invalid entries and ascending small values.
- Rows `0x8EA64-0x8EAE3` form a second ordered byte table beginning with `0xFF, 0x00, 0x01, 0x02` and continuing with selected values through `0xEF`.
- Rows `0x8EAE4-0x8EB87` are big-endian word pairs that look like offset/length or address/size descriptors.
- Rows `0x8EB88-0x8EC57` are pointer-like words into earlier firmware regions.
- Rows `0x8EC58-0x8F397` are mostly zero-filled reserved/configuration space with isolated constants.
- Rows `0x8F398-0x8F3A7` contain the final 16 bytes: `3E C0 34 51 63 75 55 54 AD 20 B6 87 AA AA AA AA`, likely trailer/checksum/signature/fill data for the firmware image.

## Dependencies

- Build-time dependencies: `uint8_t`, `_FW_LPE11002_H`, `EMLXS_FW_IMAGE_DEF`, the prior `#pragma align 8(emlxs_lpe11002_image)`, and the include path used by `emlxs_fw.h`.
- Firmware table dependency: `emlxs_fw.h` includes `fw_lpe11002.h` and places `emlxs_lpe11002_size` and `emlxs_lpe11002_image` in the `LPe11002_FW` `emlxs_firmware_t` descriptor.
- Runtime dependencies: the LPe11002 adapter firmware loader, adapter CPU ISA and endian expectations, firmware memory map, SLI1/2/3 offsets from earlier macros, mailbox/IOCB/DMA layout, and exact byte-for-byte image integrity.

## Risks and correctness notes

- Byte order and row order are semantic. Editing a single initializer can corrupt firmware behavior, pointer tables, size-sensitive descriptors, or trailer validation.
- The final size macro depends on the actual array symbol existing. Consumers must preserve the `EMLXS_FW_IMAGE_DEF` split because modular firmware builds intentionally expose `0`/`0`.
- The array is `static`; every translation unit that defines `EMLXS_FW_IMAGE_DEF` gets a private copy. The surrounding build must keep that define scoped to the firmware-table owner.
- The sparse zero-filled tail likely contains reserved firmware ABI fields. Reformatting is safe only if byte values and positions are unchanged.
- The final trailer bytes may be checksum, signature, or generator fill. They should be treated as opaque firmware metadata, not dead padding.

## Cross-chunk references

- Previous chunks contain the header preamble, metadata macros (`emlxs_lpe11002_label`, `kern`, `stub`, `sli1`-`sli4`), the array declaration, and nearly all firmware code/data before offset `0x8E8D8`.
- The immediately preceding chunk continues into this one mid-firmware routine; lines just before 73013 show ARM-like instruction bytes leading to the register-save/restore and branch sequence at the start of this chunk.
- This is the final chunk for `fw_lpe11002.h`; there is no next chunk. The file ends at line 73375.
- The per-file merge should connect this chunk’s `emlxs_lpe11002_size` and fallback macro definitions to `emlxs_fw.h` lines 138-147, where the `LPe11002_FW` table entry references the image and size.