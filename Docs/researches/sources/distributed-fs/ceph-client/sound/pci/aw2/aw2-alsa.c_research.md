# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-alsa.c

## Purpose
Provides the ALSA PCI driver wrapper for Emagic Audiowerk2 cards based on the Philips SAA7146. It handles module parameters, PCI probe, card allocation, IRQ setup, PCM device creation, PCM callbacks, and a capture route mixer control.

## Important APIs, Types, And Functions
Private structures are `aw2_pcm_device` and `aw2`. Module data includes `index`, `id`, `enable`, `snd_aw2_ids`, and `aw2_driver`. Lifecycle functions include `snd_aw2_free`, `snd_aw2_create`, and `snd_aw2_probe`. PCM callbacks include open/close/prepare/trigger/pointer for playback and capture. `snd_aw2_new_pcm()` creates analog playback, digital playback, and capture PCMs. Mixer control callbacks are `snd_aw2_control_switch_capture_info`, `get`, and `put`.

## Control Flow
`module_pci_driver()` registers `aw2_driver`. On matching SAA7146 PCI ID, probe checks card enablement, allocates a devm ALSA card, initializes PCI/MMIO/IRQ through `snd_aw2_create()`, sets names and locks, creates three PCM devices plus the capture route control, registers the card, and stores driver data. PCM prepare locks `chip->mtx`, computes period/buffer bytes, programs SAA7146 DMA, and installs period callbacks. Trigger locks `reg_lock` and starts/stops the selected SAA7146 stream. Pointer reads the helper-reported hardware byte position and converts to frames. Capture route control toggles SAA7146 GPIO between analog and digital input.

## State And Persistence
Runtime state is in `struct aw2`: embedded SAA7146 state, PCI/MMIO pointers, IRQ number, locks, ALSA card, and PCM device descriptors. ALSA runtime DMA buffers are managed by the PCM core. No driver-specific settings persist; capture route is reflected in GPIO state only.

## Dependencies And Integration Points
Depends on kernel PCI, DMA, IRQ, MMIO, module, ALSA core/PCM/control APIs, `saa7146.h`, and `aw2-saa7146.h`. It delegates all hardware register work to `aw2-saa7146.c`.

## Risks
The PCI ID matches generic Philips SAA7146 vendor/device without subsystem filtering, so probe could bind non-Audiowerk2 SAA7146 hardware if Kconfig/device matching is broad. `snd_aw2_new_pcm()` return is ignored in probe, so PCM creation failure may not abort card registration. Capture control variable is misspelled `is_disgital` but behavior is clear. The ALSA hardware descriptors require 44.1 kHz and continuous DMA buffers; unsupported runtime combinations should be rejected by ALSA constraints.

## Test Signals
Expected signals include successful probe only on real Audiowerk2 hardware, three PCM devices with correct names, 44.1 kHz S16_LE playback/capture, period callbacks on all streams, capture route control switching, and clean devm cleanup on unbind.
