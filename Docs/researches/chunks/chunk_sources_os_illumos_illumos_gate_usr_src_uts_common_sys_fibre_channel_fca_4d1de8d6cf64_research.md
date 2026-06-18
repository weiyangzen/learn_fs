# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 3335-6652

## Scope

- Researched ordered chunk 2 for `fw_lpe11000.h`, limited to lines 3335-6652 under `Docs/research_subset_a.md`.
- This range is not source-level C logic. It is a contiguous slice of the `static uint8_t emlxs_lpe11000_image[]` firmware byte initializer, covering firmware offsets `0x06768` through `0x0CF17`.
- The chunk contains 3,318 initializer lines and 26,544 image bytes. Address comments are continuous in 8-byte steps.
- The surrounding header identifies this image as `LPe11000-S: v2.82a4 (zd282a4.all)` and exposes it only when `EMLXS_FW_IMAGE_DEF` is enabled.

## APIs And Host Surface

- No new C functions, structs, typedefs, or host-callable APIs are declared in this chunk.
- The host-visible API for this file is defined outside this line range: firmware metadata macros such as `emlxs_lpe11000_label`, `emlxs_lpe11000_kern`, `emlxs_lpe11000_stub`, `emlxs_lpe11000_sli1`, `emlxs_lpe11000_sli2`, `emlxs_lpe11000_sli3`, and `emlxs_lpe11000_sli4`, plus `emlxs_lpe11000_image[]` and `emlxs_lpe11000_size`.
- `emlxs_fw.h` consumes those symbols in `EMLXS_FW_TABLE` for the `LPe11000_FW` adapter entry. This chunk contributes payload bytes to that table entry but does not affect table shape.
- Firmware-internal service routines are visible only as ARM instruction bytes. Recognizable embedded text indicates internal formatting, errno text, diagnostic output, hardware test reporting, and reset/error reporting, but these are not C APIs.

## Control Flow

- The chunk begins in the middle of firmware formatting logic. Adjacent previous lines contain uppercase hex digits and `0X`; this chunk continues with lowercase hex digits and `0x`, strongly indicating printf-style numeric formatting support.
- Repeated ARM procedure patterns are visible throughout: stack/frame setup bytes such as `E1 A0 C0 0D`, `E9 2D ...`, frame adjustment `E2 4C B0 04`, calls via `EB ...`, and returns/restores via `E9 1B ...` or `E1 A0 F0 0E`.
- Early subranges contain libc-like helpers: byte and word compare/copy loops, zero-terminated string scanning, and integer/hex formatting support.
- Around offset `0x09870` the image contains a branch table or computed dispatch fan-out for command/test IDs.
- Diagnostic/self-test control flow appears in the later half, including error-clear verification, expected/actual/error-bit reporting, invalid ALU/table-code paths, unknown pattern-generation handling, and per-register reset/test failure reporting.
- The final lines start a new firmware routine at `0x0CEF8`, but only its prologue and first few instructions are in this chunk. Its body continues in the next chunk.

## State And Data

- Embedded strings include errno text, `Error bits in ERRCLR cannot be cleared`, `Required Test`, `Unknown ALU code`, `Invalid table code`, and `Unknown pattern generation code`.
- The firmware repeatedly manipulates fields at small struct-like offsets such as `+0x04`, `+0x08`, `+0x0c`, `+0x10`, `+0x14`, `+0x18`, `+0x1c`, and `+0x20`.
- Multiple polling loops test status bits including `0x01`, `0x02`, `0x04`, `0x08`, `0x10`, `0x20`, `0x40`, and `0x80`.
- The chunk includes constants and masks used for hardware or diagnostic register manipulation, including all-ones/all-zero patterns, `0x55`/`0xaa` style test patterns, `0xff`, `0x7f`, and error/status masks.

## Dependencies

- Build dependency: requires the surrounding header context and `uint8_t`; the actual array is emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- Integration dependency: `emlxs_fw.h` includes this header and places its metadata/image pointer into the Emulex firmware table.
- Runtime dependency: the bytecode assumes the LPe11000 firmware execution environment, including ARM instruction semantics, device MMIO/register layout, mailbox or ring structures, and adapter-specific SLI firmware entry points from the header metadata.
- Tooling dependency: any loader, checksum, or relocation logic outside this file must preserve exact byte order, size, and alignment.

## Risks

- The firmware payload is opaque binary material embedded in a C header. Source-level review cannot prove memory safety, privilege boundaries, or correctness of the internal routines.
- The image likely runs on an HBA with DMA-capable hardware privileges, so firmware bugs have higher impact than ordinary host driver bugs.
- Busy-wait loops on status bits can hang firmware-side progress if hardware state never changes or if register semantics differ from expectations.
- The diagnostic/test routines visibly write patterns, clear error bits, compare reset values, and report mismatches.
- Manual edits to this chunk risk corrupting instruction alignment, jump targets, firmware offsets, size-dependent metadata, or any checksum/signature checked by the loader or device.
- The chunk boundary splits active code at both ends.

## Cross-Chunk References

- Previous chunk: provides the array declaration, firmware metadata, entry/version macros, and immediately preceding formatter code including uppercase hex formatting data around `0x06730`.
- This chunk: continues the formatter, contains libc-like helper routines, diagnostic strings, register-test/reporting code, and a command/test dispatch region.
- Next chunk: must continue from offset `0x0CF18`, completing the routine whose prologue begins at `0x0CEF8`.
- Whole file: closes the `emlxs_lpe11000_image[]` array later and defines `emlxs_lpe11000_size`; that final report should be produced only by the merge step, not by this chunk.