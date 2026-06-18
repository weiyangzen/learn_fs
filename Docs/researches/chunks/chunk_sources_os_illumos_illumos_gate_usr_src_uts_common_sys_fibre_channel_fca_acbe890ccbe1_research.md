# Chunk Research: `fw_lp11000.h` Lines 1-3335

This chunk covers the public wrapper and the first `0x6770` bytes of the embedded Emulex LP11000 Fibre Channel adapter firmware image. It is in learn_fs subset A via `sources/os/illumos/illumos-gate` from `Docs/research_subset_a.md`. I read the requested line range completely and used adjacent context only to identify the image terminator, fallback macros, and the firmware table consumer.

## APIs And Exported Data

The host-visible API in this range is small:

- Header guard `_FW_LP11000_H` and C++ linkage wrapper.
- Firmware metadata macros: `emlxs_lp11000_label`, `emlxs_lp11000_kern`, `emlxs_lp11000_stub`, and `emlxs_lp11000_sli1` through `emlxs_lp11000_sli4`.
- Under `EMLXS_FW_IMAGE_DEF`, an 8-byte-aligned `static uint8_t emlxs_lp11000_image[]` begins at line 24. This chunk contains image offsets `0x00000` through `0x0676F`.

Adjacent context shows `emlxs_fw.h` includes this header while building `EMLXS_FW_TABLE`; the metadata and image pointer populate the `LP11000_FW` entry of `emlxs_firmware_t`. The actual `emlxs_lp11000_size` macro is defined near the end of the full header, outside this chunk.

## Control Flow

There is no executable C control flow beyond preprocessor gating. The byte array contains ARM-style firmware instructions, branch vectors, literal pools, jump tables, and diagnostic strings executed by the adapter.

Visible firmware-level structures include reset/header data, vector-like instruction patterns, pointer/literal tables, a large branch dispatch table around image offset `0x011D8`, and routines that inspect fixed structure offsets, update state fields, and call helper routines. The end of this chunk is inside a printf/formatting-style routine handling `%` flags and conversions.

## State And Dependencies

The C-visible state is immutable firmware data compiled into whichever object defines `EMLXS_FW_IMAGE_DEF`. Alignment is explicit through `#pragma align 8(emlxs_lp11000_image)`.

The embedded firmware depends on the LP11000 adapter CPU, Emulex SLI firmware conventions, and on-card data structures addressed by fixed offsets. Visible strings expose debug monitor, parity/error, divide-by-zero, allocator failure, and formatting support paths.

## Risks

- A one-byte edit can corrupt instruction alignment, branch targets, literal addresses, or adapter-visible tables.
- Metadata and image bytes must stay synchronized with the `LP11000-S: v2.82a4` firmware build.
- This chunk opens `EMLXS_FW_IMAGE_DEF` and `emlxs_lp11000_image[]` but does not close them.
- Source-level C tooling cannot validate the firmware semantics.
- Consumers must account for build modes where `MODFW_SUPPORT` leaves the image pointer as the later fallback macro value.

## Cross-Chunk References

This is chunk 1, so it establishes the header contract and starts the byte array. The array continues immediately at line 3336, image offset `0x06770`, in the middle of a firmware routine. The closing brace, `emlxs_lp11000_size`, fallback image/size macros, and final preprocessor closures are outside this chunk near the end of the full file.