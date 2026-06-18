# Chunk Research: fw_lp11002.h lines 16608-19925

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`

Scope: chunk 6, lines 16608-19925, within `Docs/research_subset_a.md` (`sources/os/illumos/illumos-gate`).

## Summary

This chunk is a contiguous slice of the embedded Emulex LP11002 Fibre Channel adapter firmware image, not C control logic. The surrounding header defines `emlxs_lp11002_image[]` as a `static uint8_t` byte array when `EMLXS_FW_IMAGE_DEF` is enabled; this range contributes bytes `0x20630` through `0x26DDF` of that image. It contains 3,318 initializer lines, 26,544 bytes, and stays entirely inside the array initializer.

The first large section, offsets `0x20630-0x23C7F`, is zero-filled padding/reserved image space. Executable-looking ARM firmware words begin at line 18346 / offset `0x23C80`, with instruction patterns for loads/stores, condition checks, subroutine calls, returns, loops, and branch/jump tables. These are device firmware instructions consumed by the adapter, not instructions executed by illumos on the host CPU.

## APIs And Exposed Surface

- No new C functions, structs, typedefs, macros, or host-callable APIs are declared in this chunk.
- The relevant API surface is inherited from the file wrapper outside the chunk:
  - `emlxs_lp11002_label` identifies this firmware as `LP11002-S: v2.82a4 (bf282a4.all)`.
  - `emlxs_lp11002_image[]` is emitted only under `EMLXS_FW_IMAGE_DEF`.
  - `emlxs_lp11002_size` is `sizeof (emlxs_lp11002_image)` when the image is compiled in, otherwise zero.
- `emlxs_fw.h` includes `fw_lp11002.h` and places `emlxs_lp11002_size`, `emlxs_lp11002_image`, label, and SLI entry/version fields into the firmware table entry for `LP11002_FW`.

## Control Flow

At the C level, there is no control flow in this chunk: it is byte data in an initializer.

At the firmware-payload level, visible byte patterns are ARM-like instruction streams:

- `0x23C80` starts the non-zero code region with load/store-style words such as `E4 91 20 04` and `E4 91 30 04`.
- Around `0x24880-0x24A78`, the payload shows subroutine prologue/epilogue and call/branch patterns (`E9 2D`, `EB`, `E8 BD`, `EA`) plus repeated conditional tests and backward branches, suggesting loops over adapter-local structures or queues.
- Around `0x25C38-0x25C80`, a dense branch table dispatches among multiple local handlers.
- Around `0x266B0-0x26778`, the payload compares a byte/command field against values including `0x40`, `0x41`, `0x43`, `0x48`, `0x42`, `0x45`, `0x46`, `0x44`, `0xC1`, `0xC2`, `0xC4`, and then against symbols/punctuation-like values `0x24`, `0x20`, `0x23`, `0x25`, `0x26`, `0x27`, `0x28`, `0x29`, `0x2A`, `0xC0`, `0xC3`.
- Around `0x26780-0x26860`, jump-table-like branches are followed by absolute-looking firmware addresses such as `0x000678B0`, `0x00069298`, `0x00079990`, `0x0007F3E0`, `0x00068390`, `0x0006A750`, `0x00068EDC`, `0x00069E70`, `0x0006F99C`, and `0x0007EBC0`.
- The chunk ends mid-routine at `0x26DD8`; control-flow context continues into the next chunk.

## State And Data

- Byte range covered: `0x20630-0x26DDF`.
- Total bytes in chunk: 26,544.
- Zero-only initializer lines: 1,746.
- Non-zero initializer lines: 1,572.
- First non-zero line: line 18346, offset `0x23C80`.
- Long zero run: lines 16608-18345, offsets `0x20630-0x23C7F`, 13,904 bytes.
- Smaller zero gaps are visible at `0x23D50-0x23D67`, `0x23EE8-0x23EF7`, `0x24788-0x2478F`, and `0x24A80-0x24A8F`.
- The non-zero section manipulates firmware-local state through many offset-style byte/word accesses visible in instruction encodings, including recurring small offsets such as `0x04`, `0x07`, `0x08`, `0x0C`, `0x0E`, `0x0F`, `0x10`, `0x11`, `0x12`, `0x13`, `0x14`, `0x24`, `0x30`, `0x3C`, `0x3F`, `0x4F`, `0x50`, `0x54`, `0x56`, `0x58`, `0x6C`, `0x6D`, `0x6E`, `0x72`, `0x74`, `0x7A`, and `0x7C`, plus larger structure/table offsets such as `0x2A0`, `0x2A4`, `0x2A8`, `0x2AC`, `0x2B0`, `0x2B4`, `0x2B8`, `0x2BC`, `0x340`, `0x350`, `0x358`, `0x370`, `0x380`, `0x3C0`, and `0x704`.

## Dependencies

- Compile-time dependency: `uint8_t` must be available before this header is included, as in the surrounding emlxs driver headers.
- Inclusion/selection dependency: `EMLXS_FW_IMAGE_DEF` controls whether the image data exists in the compiled object. In `emlxs_fw.h`, this is set when building the firmware table unless `MODFW_SUPPORT` is defined.
- Runtime dependency: illumos host code treats this as opaque firmware bytes. Correct behavior depends on the adapter firmware loader consuming the byte stream exactly as generated.
- Hardware/firmware dependency: the data targets Emulex LP11002 hardware and SLI firmware metadata declared outside this chunk (`kern`, `stub`, `sli1`, `sli2`, `sli3`, `sli4`).

## Risks And Maintenance Notes

- This chunk is opaque binary firmware embedded as C initializers. Normal source review cannot prove semantic correctness without a firmware symbol map, disassembly, vendor source, or hardware validation.
- Any byte edit, line regeneration, formatter change, or truncation can corrupt firmware behavior while still compiling cleanly.
- The long zero-filled span may be intentional reserved image space or alignment. Removing or compressing it would shift offsets and break firmware-relative branches/tables.
- The header is large and conditionally compiled. Builds with `MODFW_SUPPORT` may use external firmware loading paths and compile this header with `emlxs_lp11002_image`/`size` defined as zero; code must not assume the embedded image exists in that configuration.
- Branch-table and absolute-address-looking data visible near `0x26780-0x26860` are offset-sensitive cross-references inside the firmware image. Chunk boundaries split these relationships.

## Cross-Chunk References

- Previous chunks contain the start of `emlxs_lp11002_image[]`, image header/vector data, earlier firmware code/data, and the beginning of the zero/reserved area that continues into this chunk.
- This chunk starts inside a zero/reserved area at offset `0x20630`, so its leading bytes depend on previous chunk alignment and array continuity.
- This chunk ends at offset `0x26DDF` in the middle of active firmware code; the routine and any branch targets after this point continue in chunk 7.
- File-level metadata and the array declaration/closing macros are outside this chunk and must be merged from other chunks for complete per-file documentation.