# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 6654-9971

Scope: learn_fs subset A includes `sources/os/illumos/illumos-gate`. This report covers only ordered chunk 3 of `fw_lp11002.h`. I read lines 6654-9971 completely and used adjacent context only to identify the enclosing declaration, firmware metadata macros, consumers, and chunk boundaries.

This chunk is a contiguous middle segment of the Emulex LP11002-S firmware image. It contributes byte initializer rows for `static uint8_t emlxs_lp11002_image[]` from firmware offset `0x0CF20` through `0x136CF`. The file-level header identifies the image as `LP11002-S: v2.82a4 (bf282a4.all)`, with `kern`, `stub`, and SLI revision constants defined before the array. The array is compiled only when `EMLXS_FW_IMAGE_DEF` is defined.

## Host-visible API surface

- No C functions, structs, typedefs, enums, callbacks, locks, or driver entry points are introduced in this chunk.
- The only host-visible symbol affected is the existing `emlxs_lp11002_image[]` byte array declared earlier in the file.
- The chunk does not define `emlxs_lp11002_size`; that macro appears at the final array close in a later chunk.
- The chunk has no independent include or macro dependencies beyond the already-open `EMLXS_FW_IMAGE_DEF` branch and `uint8_t` array declaration.

## Control flow

Host C control flow is only the enclosing compile-time choice: with `EMLXS_FW_IMAGE_DEF`, these lines become part of the embedded firmware image; without it, this segment is skipped and later fallback macros expose a null image and zero size.

Inside the firmware payload, the rows are ARM-like instruction bytes with frequent branch/call words, stack/register save and restore patterns, conditional branches, comparisons, loads, stores, and loops. The apparent firmware-side routines include list/ring traversal, buffer or descriptor accounting, register manipulation, memory copy/fill style loops, and diagnostics. The chunk starts and ends mid-routine, so several control-flow edges cross chunk boundaries.

## State and dependencies

- Firmware offsets covered: `0x0CF20-0x136CF`, equal to `0x67B0` bytes.
- Around `0x133F8-0x13490`, embedded diagnostic strings cover bit-pattern tests.
- Around `0x13568-0x13608`, embedded error strings mention SMISR failures.
- Dependencies include `uint8_t`, `_FW_LP11002_H`, `EMLXS_FW_IMAGE_DEF`, `emlxs_fw.h`’s `LP11002_FW` firmware table entry, `emlxs_adapters.h` LP11002 adapter mappings, and exact adapter firmware ABI expectations.

## Risks and cross-chunk references

Byte order, row order, and exact offsets are semantic; editing any initializer byte can corrupt firmware behavior. The diagnostic text is firmware data, not removable host logging. Earlier chunks define the metadata and array start; the next chunk continues the diagnostic routine after the SMISR strings; a later final chunk closes the array and defines `emlxs_lp11002_size` as the full `0x8DCB8` image size.