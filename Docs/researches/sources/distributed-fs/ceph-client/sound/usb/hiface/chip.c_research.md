# sources/distributed-fs/ceph-client/sound/usb/hiface/chip.c

## Purpose
Implements USB driver registration, ALSA card creation, probe, disconnect, and device ID quirks for M2Tech hiFace-compatible USB-SPDIF devices.

## Important APIs and Functions
The module exposes a `usb_driver` through `module_usb_driver()`. `hiface_chip_probe()` sets interface 0 altsetting 0, finds an enabled ALSA card slot, creates the card, initializes PCM via `hiface_pcm_init()`, registers the card, and stores interface data. `hiface_chip_disconnect()` disconnects the ALSA card, aborts PCM, and frees when closed. `hiface_chip_create()` fills ALSA card driver/shortname/longname and initializes `struct hiface_chip`.

## Control Flow and State
Probe is serialized by `register_mutex` while selecting an enabled index. Vendor-specific `driver_info` provides user-facing device names and an `extra_freq` flag for 352.8/384 kHz support. Disconnect prevents new user-space operations with `snd_card_disconnect()`, stops USB playback through `hiface_pcm_abort()`, then defers free until open handles close.

## Dependencies and Integration
Depends on ALSA card APIs, Linux USB module/device tables, `chip.h`, and `pcm.h`. The device table covers many vendor/product IDs that share the hiFace protocol.

## Risks and Test Signals
Risks include simplistic card-slot selection that does not mark slots consumed in this file, errors after `snd_card_new()` requiring correct cleanup, and device table quirk mistakes. Tests should cover probing multiple matching devices, disabled module slots, extra-frequency devices, disconnect during playback, and module unload.
