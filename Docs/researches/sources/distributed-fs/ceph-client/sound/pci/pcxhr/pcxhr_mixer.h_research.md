# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.h

## Purpose

This header exposes the mixer creation entry point for the PCXHR driver.

## Important APIs, Types, And Functions

- `pcxhr_create_mixer(struct pcxhr_mgr *mgr)` creates ALSA controls for every logical card managed by the physical PCI board.

## Control Flow

Firmware setup calls `pcxhr_create_mixer()` after DSP firmware has loaded, board options have been detected, pipes have been allocated, and PCM devices have been created. The mixer implementation then adds controls based on `mgr` and per-card capabilities.

## State And Persistence

No state is stored in the header. The function it declares initializes and populates in-memory mixer state in `pcxhr_mgr` and `snd_pcxhr`.

## Dependencies And Integration Points

It is included by `pcxhr.c`, `pcxhr_core.c`, `pcxhr_hwdep.c`, and `pcxhr_mixer.c`. The declaration keeps mixer setup independent from the main probe and firmware setup files.

## Risks

Because the header exposes only one entry point, all feature gating and error handling are inside `pcxhr_mixer.c`. Callers must invoke it only after firmware is ready to accept DSP commands.

## Test Signals

Compilation verifies the declaration; runtime probe should show expected mixer controls after firmware load and no mixer creation before the DSP command path is available.
