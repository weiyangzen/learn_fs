# sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.h

## Purpose
Declares the hiFace PCM layer entry points used by the USB probe/disconnect layer.

## APIs and Integration
`hiface_pcm_init(struct hiface_chip *chip, u8 extra_freq)` creates ALSA playback PCM state and URBs. `hiface_pcm_abort(struct hiface_chip *chip)` stops streaming and prevents further PCM work after disconnect or fatal errors.

## State, Dependencies, and Risks
The implementation stores runtime state in `chip->pcm`; callers must pass a valid `hiface_chip` with a live USB device and ALSA card. Abort must be safe during disconnect and while callbacks are outstanding.

## Test Signals
Build coverage and probe/disconnect/playback tests validate the public contract.
