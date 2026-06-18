# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 1-3335

## Scope

This report covers only chunk 1 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`, lines 1-3335, in learn_fs subset A (`Docs/research_subset_a.md`). I read the full requested line range and used adjacent context only to identify the enclosing firmware table consumer and the full-image footer. This chunk contains the C wrapper and the first `0x6770` bytes of an embedded Emulex LP11002 firmware image; it is mostly ARM firmware bytes, not normal driver C logic.

## APIs And Exported Data

The host-visible API surface in this chunk is a header-only firmware descriptor:

- Lines 7-24 define the include guard, optional C++ linkage, LP11002 label, firmware entry/revision constants, and aligned `static uint8_t emlxs_lp11002_image[]` under `EMLXS_FW_IMAGE_DEF`.
- The visible payload covers firmware offsets `0x00000` through `0x06768`.
- Adjacent footer context shows the full image is `0x8DCB8` bytes and later defines `emlxs_lp11002_size` or zero fallback macros.

## Control Flow

At the host C level, there is no runtime control flow, only preprocessor selection for emitting or suppressing the firmware image.

At the firmware level, the byte stream is ARM code and data. It includes initial header/padding, vector-like load-to-PC entries, branch tables, dispatcher stubs, pointer tables, byte-classification/mask tables, and executable routines with stack saves/restores, loads/stores, loops, conditional branches, and calls to other firmware offsets.

The chunk ends mid-routine at firmware offset `0x06768`; chunk 2 continues the instruction stream.

## State And Dependencies

Host-visible state is immutable firmware metadata plus the static byte array. It depends on `uint8_t`, `EMLXS_FW_IMAGE_DEF`, illumos `#pragma align 8`, and `emlxs_fw.h`, whose firmware table consumes `emlxs_lp11002_size`, `emlxs_lp11002_image`, label, and `kern`/`stub`/`sli*` constants for `LP11002_FW`.

Firmware-internal state is opaque but visibly uses fixed control-block/register-like offsets such as `0x50`, `0x54`, `0x58`, `0x68`, `0x69`, `0x6a`, `0x6b`, `0x734`, `0x738`, `0x764`, `0x768`, and `0x7a4`.

## Visible Embedded Strings And Diagnostics

Visible strings include `Unknown Error`, `Divide by zero`, `EMULEX Helios RAM Debug Monitor, V1.00`, several `[B/H ... DeMon]` monitor strings, `PE with Pattern: ...`, `PE in Byte: ...`, `No store left for I/O buffer or the like`, `*** Fatal error in run-time system:`, `malloc failed`, `free failed`, `_coalesce failed`, `realloc failed, (bad user block)`, and `Couldn't write`.

## Risks

The primary risk is binary integrity: any initializer edit can silently alter adapter firmware while still compiling. Metadata constants must remain synchronized with the payload or firmware selection/loading may fail. The `EMLXS_FW_IMAGE_DEF` split is build-sensitive: multiple definitions duplicate a large static image, while missing it leaves only the zero-image fallback.

Because this is vendor/generated firmware data, source review cannot prove firmware memory safety or protocol correctness; verification needs byte comparison, provenance checks, build/link checks, and driver-level firmware load tests.

## Cross-Chunk References

This is the first chunk, so no earlier chunk is needed for the prologue or image start. Chunk 2 must continue the mid-routine boundary and nearby formatting/string data. Later chunks are required for the remaining firmware body, final image close, `emlxs_lp11002_size`, fallback macros, and closing guards.