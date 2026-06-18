# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 6654-9971

## Scope

This chunk is ordered chunk 3 of `fw_lp11000.h`, covering source lines 6654-9971. It is entirely inside `static uint8_t emlxs_lp11000_image[]`, gated by `EMLXS_FW_IMAGE_DEF`. The firmware byte offsets run from `0x0CF20` through `0x136CF`, ending mid-routine/data stream; line 9972 continues at `0x136D0`.

The file-level header identifies this as Emulex LP11000-S firmware `v2.82a4 (bd282a4.all)`. This chunk adds no host C functions, structs, or macros; it contributes opaque firmware bytes consumed through `emlxs_lp11000_image` and `emlxs_lp11000_size`.

## APIs And Integration Surface

- Host-visible API: none in this range.
- File-level API: bytes are part of `emlxs_lp11000_image[]`.
- Build gate: included only when `EMLXS_FW_IMAGE_DEF` is defined; otherwise image and size are `0`.
- Consumer path: `emlxs_fw.h` includes `fw_lp11000.h` and builds the `LP11000_FW` `emlxs_firmware_t` table entry with size, image pointer, label, and SLI/kern/stub values.

## Firmware Content

This is ARM-style firmware bytecode/data. Visible content includes queue/list traversal patterns, low-level memory/register access, and embedded diagnostics.

Notable strings and diagnostics in this chunk:

- `PCI Configuration Test`
- `Local Memory SRAM Test`
- `On-Chip RAM Test`
- `SLIM Test`
- `World Wide Port Name Test`
- `Timer Test`
- Memory pattern tests using all-zero bits, all-one bits, mostly `5`, mostly `A`, and address-as-data.
- SMISR error diagnostics for uncleared error bits, write pass, read pass, and address read pass.
- Embedded Emulex copyright string at firmware offset `0x12460`.

## Control Flow

At the C level, there is no executable control flow; this is a constant initializer. The embedded firmware shows:

- The chunk begins mid-function, relying on setup in the previous chunk.
- Repeated ARM prologue/epilogue patterns and relative branch/call encodings.
- Loops over apparent ring/list structures using offsets such as `0x60`, `0x68`, `0x70`, `0x08`, `0x10`, `0x1C`, and `0x20`.
- Diagnostic dispatch around `0x12D58-0x12EE8`, matching the nearby test-label strings.
- SMISR/address-read diagnostic logic begins near `0x13498` and continues past this chunk.

## State And Dependencies

State is firmware-private and opaque to illumos C code. The bytecode appears to manipulate adapter register bases, firmware queues/lists, stack-local command/test descriptors, counters, flags, and pointers to diagnostic strings.

Dependencies:

- `fw_lp11000.h` preprocessor context and image array declaration.
- `emlxs_fw.h` firmware table definitions.
- LP11000 adapter hardware layout: PCI config space, SRAM/SLIM memory, WWPN storage, timers, and SMISR/status registers.
- Earlier and later bytes in `emlxs_lp11000_image[]`; this chunk is not standalone.

## Risks

- Opaque firmware cannot be meaningfully safety-reviewed without disassembly, symbols, vendor docs, or hardware validation.
- Chunk boundaries split routines: previous chunk provides setup, next chunk completes the active diagnostic path.
- Any byte, alignment, or comma-format edit may corrupt firmware while still compiling.
- Security/reliability risk sits in firmware download/execution: host driver loads this opaque low-level code into the HBA.
- Provenance is vendor-specific Emulex firmware under the file’s referenced license terms.

## Cross-Chunk References

- Previous chunk: required for setup before `0x0CF20`; lines 6648-6653 show preceding prologue/setup.
- Next chunk: required after line 9971; `0x136D0` continues the SMISR/address-read diagnostic routine.
- File-level header/footer outside this chunk define public metadata macros, image declaration, size macro, and zero fallback macros.