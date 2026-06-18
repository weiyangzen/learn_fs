# sources/distributed-fs/ceph-client/sound/ppc/powermac.c

## Purpose

This file is the ALSA platform-driver wrapper for legacy PowerMac onboard audio. It creates the ALSA card, invokes low-level PowerMac detection/setup, dispatches to the proper codec initializer, creates PCM and optional beep support, registers the card, and bridges platform PM callbacks.

## Important APIs, types, and functions

`snd_pmac_probe()` is the platform probe entry. It calls `snd_card_new()`, `snd_pmac_new()`, codec initializers (`snd_pmac_awacs_init()`, `snd_pmac_burgundy_init()`, `snd_pmac_daca_init()`, `snd_pmac_tumbler_init()` plus post init), `snd_pmac_pcm_new()`, optional `snd_pmac_attach_beep()`, and `snd_card_register()`. Module init registers `snd_pmac_driver` and a simple platform device named `snd_powermac`.

## Control flow

Module init registers the driver then creates a matching platform device to force probe on supported PowerMac systems. Probe switches on `chip->model`, fills card names, initializes codec-specific mixer/hardware, creates PCM, marks the chip initialized, optionally attaches beep, and registers the card. Remove frees the card. PM sleep callbacks forward to `snd_pmac_suspend()` and `snd_pmac_resume()`.

## State and persistence behavior

Global `device` stores the synthetic platform device. Module parameters persist requested ALSA index/id and whether PCM beep is enabled. Per-card state is stored as `card->private_data`.

## Dependencies and integration points

It depends on Linux platform driver APIs, ALSA module/card APIs, and all PowerMac codec entry points linked by the Makefile. It is the visible module boundary for `snd-powermac`.

## Risks and test signals

Risks include registering the synthetic device even if driver registration succeeded but device creation failed, codec switch naming drift, and error unwind depending on `snd_card_free()` to release partially initialized low-level resources. Test module load/unload, unsupported hardware path, each codec model, `enable_beep=0/1`, and platform suspend/resume.
