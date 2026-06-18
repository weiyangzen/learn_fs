# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1.c

## Purpose

`emu10k1.c` is the PCI driver entry point for Creative EMU10K1, Audigy, and Audigy 2 family ALSA cards. It declares module parameters, PCI IDs, probe sequencing, optional wavetable sequencer setup, and power-management callbacks.

## Important APIs, Types, and Functions

Module parameters control ALSA card index/id/enable, FX8010 external input/output masks, sequencer ports, max synth voices, max sample buffer size, IR enablement, and forced subsystem model. `snd_emu10k1_ids` matches Creative PCI device IDs `0002`, `0004`, and `0008`. `snd_card_emu10k1_probe()` creates the ALSA card, clamps sample cache size, calls `snd_emu10k1_create()`, registers PCM devices, mixer, timer, multi-channel PCM, optional P16V PCM, MIDI, FX8010, and optional synth sequence device. `snd_emu10k1_suspend()` and `snd_emu10k1_resume()` save/restore AC97, FX, registers, P16V, and hardware init state. `module_pci_driver()` registers the PCI driver.

## Control Flow

Probe skips disabled slots, allocates a devm-managed ALSA card, initializes hardware through `snd_emu10k1_create()`, then layers ALSA devices in dependency order: PCM, mixer, timer, multi, P16V, MIDI, FX8010, and synth. It fills card names and registers the card. Suspend cancels E-MU work, suspends subdevices, saves registers, and shuts down hardware; resume reinitializes hardware, restores FX/AC97/registers/P16V, and returns the card to D0.

## State and Persistence Behavior

Static state includes module parameter arrays and the PCI ID table. Per-card state is in `struct snd_emu10k1` stored as `card->private_data`. Power management persists register snapshots through helpers in `emu10k1_main.c`.

## Dependencies and Integration Points

It depends on ALSA core/initval, PCI APIs, `sound/emu10k1.h`, optional sequencer support, and many driver-internal creation functions implemented in sibling files.

## Risks and Test Signals

Risks include partial probe ordering bugs, missing cleanup on intermediate failures, invalid module parameters, and PM restore ordering regressions. Test signals are probe on supported PCI IDs, all ALSA devices appearing, synth device creation with sequencer enabled, suspend/resume with active PCM, and correct behavior with P16V/Audigy variants.
