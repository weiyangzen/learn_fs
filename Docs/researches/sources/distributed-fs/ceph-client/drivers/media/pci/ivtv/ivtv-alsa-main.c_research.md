# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-main.c

## Purpose
`ivtv-alsa-main.c` registers an ALSA capture card for each ivtv device with an enabled PCM stream. It hooks into the ivtv extension init callback, creates `struct snd_ivtv_card`, creates the PCM device, registers the ALSA card, and tears cards down during module unload.

## Important APIs, Types, And Functions
The file defines module parameters `debug` and `index[]`, global `ivtv_alsa_debug`, and helper functions `snd_ivtv_card_create()`, `snd_ivtv_card_set_names()`, `snd_ivtv_init()`, `ivtv_alsa_load()`, `snd_ivtv_exit()`, and `ivtv_alsa_exit_callback()`. It uses `struct snd_ivtv_card` from `ivtv-alsa.h` and `snd_ivtv_pcm_create()` from `ivtv-alsa-pcm.c`.

## Control Flow
Module init sets `ivtv_ext_init` to `ivtv_alsa_load`, letting the main ivtv driver call into ALSA setup for each card. `ivtv_alsa_load()` skips disabled PCM streams and duplicate ALSA instances, then calls `snd_ivtv_init()`. Card initialization creates an ALSA card, attaches private data, sets driver/short/long names, creates the PCM capture device, stores `itv->alsa` before registration to avoid races, and registers the card.

Module exit finds the `ivtv` PCI driver, iterates devices, retrieves each V4L2 device's ALSA card, frees the ALSA card, clears `itv->alsa`, and clears `ivtv_ext_init`.

## State And Persistence
State is live module/device state only: `itv->alsa` links ivtv to ALSA private data, and ALSA card lifetime is managed by `snd_card_free()`. Module parameters persist only while loaded.

## Dependencies And Integration Points
The file integrates ivtv core, V4L2 device state, ALSA core, PCI driver iteration, and the PCM implementation.

## Risks And Test Signals
In `snd_ivtv_init()` error handling, `snd_card_free(sc)` will call private free after `snd_ivtv_card_create()`, then the code also `kfree(itvsc)`, creating a potential double free. Module exit calls `driver_find()` without checking for NULL before `driver_for_each_device()`. Tests should cover PCM-disabled cards, duplicate load, ALSA registration failure, module unload while cards exist, and KASAN/KFENCE around error paths.
