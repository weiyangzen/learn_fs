# sources/distributed-fs/ceph-client/sound/pci/trident/trident.c

## Purpose
This file is the PCI/module wrapper for the Trident 4DWave DX/NX and SiS SI7018 ALSA driver. It declares module parameters and PCI IDs, allocates the ALSA card, calls the shared device constructor in `trident_main.c`, creates device-specific PCM/MIDI/gameport surfaces, and registers the card.

## Important APIs, types, and functions
Module parameters are `index`, `id`, `enable`, `pcm_channels`, and `wavetable_size`. Supported IDs are Trident 4DWave DX, Trident 4DWave NX, and SiS 7018. The only substantive function is `snd_trident_probe()`. It calls exported helpers declared in `trident.h`: `snd_trident_create()`, `snd_trident_pcm()`, `snd_trident_foldback_pcm()`, `snd_trident_spdif_pcm()`, and `snd_trident_create_gameport()`. It also optionally creates an integrated MPU-401 UART for non-SiS devices.

## Control flow
The PCI driver invokes `snd_trident_probe()` for matching devices. The function enforces the `SNDRV_CARDS` index limit and per-card `enable` flag, allocates an ALSA card with `struct snd_trident` private data, and calls `snd_trident_create()`. The `pcm_spdif_device` argument is `1` for SiS7018 and `2` for Trident devices so later IEC958 controls bind to the right PCM device index.

After core creation, the wrapper selects card driver strings by detected device, creates the main PCM, creates foldback PCM only for DX/NX, creates S/PDIF PCM only for NX/SI7018, creates MPU-401 only for non-SiS devices, attempts gameport creation, registers the card, stores PCI driver data, and increments the static card index.

## State and persistence behavior
The file has little runtime state beyond module-parameter arrays and the static `dev` probe counter. Device state lives in `struct snd_trident`, allocated by `snd_devm_card_new()` and initialized by `trident_main.c`. No suspend/resume code is implemented here, but the PCI driver attaches `snd_trident_pm` when `CONFIG_PM_SLEEP` is enabled.

## Dependencies and integration points
This wrapper integrates Linux PCI matching, ALSA card allocation, ALSA MPU-401 UART support, module parameters, and the shared Trident implementation. It depends on `trident.h` for device IDs, private structure declarations, helper prototypes, and PM ops.

## Risks and test signals
Risks include static `dev` indexing behavior across disabled cards, device-specific PCM ordering assumptions, and best-effort gameport creation whose failure is ignored. Test signals include probe for each of DX, NX, and SI7018, correct card names, expected PCM device count/order, absence of MPU-401 on SI7018, presence of S/PDIF on NX/SI7018, and PM ops being present in builds with sleep support.
