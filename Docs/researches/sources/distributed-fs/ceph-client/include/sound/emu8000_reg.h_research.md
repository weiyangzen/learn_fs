# sources/distributed-fs/ceph-client/include/sound/emu8000_reg.h

## Purpose
This header maps EMU8000 hardware register operations into readable read/write macros.

## Important APIs, Types, and Constants
It defines port accessors `EMU8000_DATA*()` and `EMU8000_PTR()`, command composition `EMU8000_CMD(reg, chan)`, a full set of `*_READ()` and `*_WRITE()` macros for channel registers, hardware config registers, sample memory address/data registers, envelope/LFO/filter/pitch registers, and initialization registers.

## Control Flow
The EMU8000 implementation uses these macros to route all hardware register I/O through lower-level `snd_emu8000_peek/poke` and word/dword variants. Per-channel operations pass a channel number into command encoding, while global operations pass fixed register IDs.

## State and Persistence
State is entirely in EMU8000 hardware registers and on-board RAM. The macros do not cache state or validate sequencing.

## Dependencies and Integration Points
The macros require a `struct snd_emu8000` pointer and lower-level poke/peek functions declared in `emu8000.h`/implementation. They integrate with voice programming, sample memory transfer, effects, and initialization code.

## Risks and Edge Cases
Macros evaluate arguments directly and perform hardware I/O side effects. Wrong channel/register values program unrelated voice state. There is no locking in the macros, so callers must serialize access around shared hardware ports.

## Test Signals
Unit-style compile coverage, register access smoke tests on hardware/emulator, concurrent voice programming under driver locks, and suspend/resume reprogramming are the main signals.
