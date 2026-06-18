# Chunk Research: fw_lp10000.h lines 9972-13289

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h`
Chunk: 4, firmware-image offsets approximately `0x136D0` through `0x19E78`.

## Scope And Form

This chunk is not C logic in the usual sense. It is a contiguous slice of the `static uint8_t emlxs_lp10000_image[]` firmware payload for the Emulex LP10000 adapter. The C-visible API surface remains the image array declared earlier in the file; this chunk contributes ARM firmware instructions, embedded strings, jump tables, and configuration/test data consumed after the driver downloads the image.

## Visible Firmware Subsystems

- Memory and register diagnostics dominate the first part of the chunk. Embedded diagnostics include tests with all-zero/all-one patterns, mostly `5`/`A` digit patterns, address-as-data passes, SMISR error checks, local SRAM, on-chip RAM, SLIM, DMA, and DTCM test labels.
- A built-in `EMULEX Thor NoRAM Debug Monitor, V01.00` appears around offsets `0x149D8`-`0x15CD8`. It includes command prompts, invalid input handling, exception labels, register display labels, status/flag formatting, and command words like halt/ignore/skip/no RAM.
- Hardware bring-up and self-test code later configures GigaBlaze/SerDes, NL_PORT, PCS, PCFG, and LPST state. Strings show internal/external SerDes detection, loopback tests, no-wrap variants, NLPORT init, monitoring-state waits, and PCS polling for `0x00F08400`.

## APIs And Interfaces

- No new C functions, macros, structs, typedefs, or exported symbols are defined in this chunk.
- Firmware-side interfaces are MMIO/register protocols rather than C APIs. Repeated patterns access apparent register regions around `0x0Axx`, `0x09xx`, `0x2600`-relative offsets, and `0x302`-style blocks.
- Several routines use a shared print/log helper pattern: load embedded string address, pass a small width/count such as `0x08`, then branch to a common helper outside this chunk.
- The debug monitor exposes an implicit serial/console command interface with display/register operations and single-letter command parsing.

## Control Flow

- The chunk begins mid-routine from the previous chunk, continuing a repetitive write/test sequence over register offsets `0x64`, `0x68`, and `0x6C`.
- It contains multiple ARM function prologues/epilogues and many direct branch-with-link calls; most callees are outside this chunk.
- Execution alternates between instruction blocks and embedded data/string pools. Jump tables reference firmware-relative addresses such as `0x0001302C`, `0x00013C00`, `0x00013EC8`, `0x0001409C`, `0x00014210`, `0x00014F34` through `0x00015AB0`, and monitor dispatch tables around `0x161D8`-`0x16250`.
- Later NLPORT/SerDes routines are polling-heavy: they write config registers, delay/spin for fixed loop counts, poll PCS/PCFG bits, and continue or return status.

## State And Data

- Visible state includes test counters, expected/found compare values, memory bounds, register snapshots, CPU mode/register-bank snapshots, PCS/PCFG/GBCTL/LPST values, SerDes loopback flags, and NL_PORT flags.
- Data tables include diagnostic patterns (`0x11111111` through `0xEEEEEEEE`, `0xAAAAAAAA`, `0xBBBBBBBB`, `0xBD/BE`, `0x7D/7E`), pointer tables, and descriptor/config tables around `0x19000`-`0x193C0`.
- Final-section diagnostics include `NLPort5 LoopBack`, `NLPORT+ LB1`, `Data miscompare at address`, `Expected`, `Found`, SerDes detection, GigaBlaze loopback modes, `No_nlportWRAP_Set1gig/Set2gig`, `nlportWRAP_Set2gig`, `NLPORT_INIT:PCFG`, and `Issuing LPST_INIT`.

## Dependencies And Risks

- Depends on adjacent firmware chunks for routine entry points, shared print/log helpers, MMIO helpers, branch targets, and routine continuation.
- Depends on the host driver preserving byte order, offsets, and array contents exactly when compiling and downloading `emlxs_lp10000_image[]`.
- This is opaque privileged firmware; source-level review cannot prove memory safety or register correctness. Any byte edit can corrupt executable firmware or data.
- The debug monitor may expose low-level register/memory access if reachable in production. Polling loops may hang if PCS/SerDes/NL_PORT state bits never converge.

## Cross-Chunk References

- Entry into this chunk comes from a routine started before line 9972.
- Jump tables point back to offsets before this chunk, including `0x12FAC`, `0x13004`, and `0x13020`.
- Many branch-with-link instructions target earlier helpers for printing, compare reporting, delay, memory fill/copy, and register access.
- The chunk ends mid-NLPORT initialization after PCS reads; final handling continues in the next chunk.