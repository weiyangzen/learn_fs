<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-usb.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-usb.h

## Purpose
`soc-usb.h` defines the ASoC USB offload interface, allowing SoC audio components to track USB sound devices, query supported formats, set up offload jack reporting, and expose route controls for card/PCM mapping.

## Important APIs, types, and functions
`enum snd_soc_usb_kctl` distinguishes card-route and PCM-route controls. `struct snd_soc_usb_device` records USB sound card index, chip index, capture/playback PCM index arrays, stream counts, and list node. `struct snd_soc_usb` represents a SoC USB backend with component pointer, connection-status callback, offload-route callback, private data, and list node. Enabled APIs include `snd_soc_usb_find_supported_format()`, connect/disconnect, private-data lookup, offload jack setup, offload route update, and port allocate/free/add/remove. Disabled builds return `-EINVAL`, `-ENODEV`, `NULL`, no-op, or `ERR_PTR(-ENOMEM)`.

## Control flow
A SoC component allocates and registers a USB offload port. USB audio code notifies connect/disconnect with `snd_soc_usb_device`; the SoC backend updates route controls, validates PCM formats, and may report jack/offload status through ASoC jack integration.

## State and persistence behavior
Runtime state consists of registered SoC USB ports and connected USB sound-device records with PCM index arrays. It is in memory only and changes with USB hotplug.

## Dependencies and integration points
It depends on ASoC components/cards/jacks and ALSA PCM params. It integrates USB audio devices with SoC DSP/offload routing.

## Risks and test signals
Risks include disabled-feature stubs returning confusing values, capture path marked untested, stale PCM index arrays on disconnect, route-control direction mistakes, hotplug races, and private-data lookup lifetime. Test signals include USB playback offload connect/disconnect, format matching, route kcontrol updates for card and PCM paths, jack setup, multiple USB devices, capture placeholders, and disabled `CONFIG_SND_SOC_USB` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-usb.h -->
