# Chunk Research: fw_lp11000.h lines 9972-13289

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h`  
Scope: `Docs/research_subset_a.md`  
Chunk: 4, lines 9972-13289, firmware offsets `0x136D0` through `0x19E78`

## Role In File

This chunk is entirely inside the `static uint8_t emlxs_lp11000_image[]` initializer, compiled only when `EMLXS_FW_IMAGE_DEF` is set. It contributes about 26,544 bytes of the embedded LP11000 firmware image. It does not define C functions, C structs, macros, or callable host-side APIs on its own.

The host-visible API is the surrounding file-level symbol set: `emlxs_lp11000_image[]`, `emlxs_lp11000_size`, firmware label, and kern/stub/SLI version constants.

## Dependencies And Consumers

`emlxs_fw.h` includes this header while building `EMLXS_FW_TABLE`; the LP11000 table entry points at this image and metadata. `emlxs_adapters.h` maps LP11000 variants to `LP11000_FW`, selecting this firmware.

## Encoded Control Flow

The chunk contains ARM-like firmware instructions plus literal/data regions. It starts mid-routine at `0x136D0` and ends in active instruction bytes at `0x19E78`; the next chunk continues at `0x19E80`.

Visible firmware regions include memory-test loops, SRAM/QDR/SLIM diagnostics, an Emulex Helios NoRAM debug monitor, register/status display text, repeated test-pattern data, and a likely literal/vector/config table around `0x19D48-0x19DAF`.

## Encoded State And Diagnostics

Embedded strings expose firmware state for memory testing, SRAM capacity, QDR/local SRAM registers, DXB queues, DTCM, on-chip RAM failures, SMISR errors, SLIM testing, and debug monitor state such as `ABORT`, `Halt`, `Ignore`, `CPSR`, `SPSR`, `UNDEF`, and `USER`.

These are firmware-resident diagnostics, not direct illumos driver log strings.

## Risks And Cross-Chunk Notes

This is opaque vendor firmware stored as a C byte initializer. Byte changes risk corrupting firmware behavior, version identity, checksums, or load addresses. The chunk mixes instructions and data, so it should not be treated as homogeneous code.

Previous chunk contains the routine lead-in and SMISR strings before `0x136D0`; next chunk continues the active instruction stream from `0x19E80`. This report should be merged into the per-file firmware-image report, not treated as a standalone driver module.