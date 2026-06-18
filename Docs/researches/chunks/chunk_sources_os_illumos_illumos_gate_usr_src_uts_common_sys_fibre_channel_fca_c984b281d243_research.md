# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h lines 46469-49786

## Scope

This report covers chunk 15 of `fw_lpe12000.h` for learn_fs subset A (`Docs/research_subset_a.md`). The requested line range `46469-49786` was read completely. Adjacent context was used only to identify the enclosing header, the firmware-table consumer, and neighboring chunk boundaries.

The chunk is entirely inside the generated `static uint8_t emlxs_lpe12000_image[]` initializer for the Emulex LPe12000 Fibre Channel adapter firmware. It is opaque firmware bytecode/data, not ordinary illumos host-side C implementation.

This line range covers firmware-image rows `0x5AB58` through `0x61300`, ending at byte `0x61307`. The covered byte interval is `[0x5AB58, 0x61308)`, for 26,544 bytes of the full `0x75C0C` byte image.

## APIs And Exported Data

This chunk defines no C functions, structs, typedefs, enums, callbacks, macros, or host-callable driver APIs. Its only host-visible contribution is contiguous byte content in `emlxs_lpe12000_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.

The C-visible firmware contract is outside this chunk: `emlxs_lpe12000_label`, `emlxs_lpe12000_kern`, `emlxs_lpe12000_stub`, SLI compatibility/address macros, and `emlxs_lpe12000_size`. `emlxs_fw.h` includes this header when building the firmware table and maps `LPe12000_FW` to the image pointer, image size, label, and metadata constants.

## Control Flow

There is no illumos kernel control flow in this range. The host compiler sees only byte initializers.

The byte stream has ARM-like firmware instruction structure: register-save prologues, restores/returns, branches, calls, loads/stores, and immediate compare/mask operations. Several local dispatch blocks compare small state/opcode bytes, especially fields at offset `0x07`, against values such as `0x5A`-`0x5F`, `0x72`-`0x74`, `0x7B`-`0x7F`, `0x90`-`0x9E`, `0xA0`-`0xA9`, `0xB0`, and `0xB1`.

Visible embedded strings mark firmware diagnostic paths rather than host messages, including `T/O x %x %x`, `BIUE: %08x`, `Reset DMA, no DMA queued`, and `Reset DMA, need all DMA queued %d`.

## State, Dependencies, Risks, Cross-Chunk References

At the C level, this chunk has no mutable host state, initialization side effects, locks, memory allocation, reference counts, or direct access to illumos kernel objects. Compile-time dependencies are inherited from the enclosing header: `uint8_t`, `_FW_LPE12000_H`, `EMLXS_FW_IMAGE_DEF`, and `#pragma align 8(emlxs_lpe12000_image)`.

Runtime dependency is indirect and hardware-specific: the `emlxs` firmware-loading path consumes the full `emlxs_lpe12000_image[]` through the `LPe12000_FW` table entry and downloads it to compatible adapter hardware.

Main risk: any byte edit can preserve C syntax while corrupting firmware instructions, branch targets, literal pools, diagnostics, or device-side state handling. Chunk 14 ends at `0x5AB57`; this chunk starts at `0x5AB58`. Chunk 16 starts at `0x61308`; this chunk ends at `0x61307`. The final per-file merge should treat this as one segment of the opaque LPe12000 firmware image, not as an independent C module.