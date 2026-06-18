# sources/distributed-fs/ceph-client/sound/usb/hiface/chip.h

## Purpose
Defines the shared hiFace chip object used by the probe and PCM layers.

## Types and Integration
`struct hiface_chip` stores the USB device pointer, ALSA card pointer, and private `pcm_runtime` pointer. `pcm_runtime` is forward-declared so `chip.c` does not need PCM internals. `pcm.c` owns allocation and teardown of `chip->pcm`.

## State and Risks
The struct is embedded in ALSA card private data. Lifetime is tied to `snd_card_new()`/`snd_card_free_when_closed()`. Risks are stale `chip->pcm` on partial PCM initialization failure or disconnect while callbacks still reference the chip; `hiface_pcm_abort()` and card disconnect mitigate this.

## Test Signals
Compile coverage plus probe/disconnect/playback tests validate that both layers agree on the shared structure.
