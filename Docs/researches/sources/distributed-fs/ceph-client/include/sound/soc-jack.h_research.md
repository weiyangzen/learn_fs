<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-jack.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-jack.h

## Purpose
`soc-jack.h` defines ASoC jack reporting, including jack pins, ADC voltage zones, GPIO detection, notifiers, and ALSA jack status propagation.

## Important APIs, types, and functions
`struct snd_soc_jack_pin` maps status masks to DAPM pins with optional inversion. `struct snd_soc_jack_zone` maps voltage ranges to jack types and debounce times. `struct snd_soc_jack_gpio` describes GPIO-backed detection, wake, debounce, delayed work, notifier, descriptor, private data, and optional status callback. `struct snd_soc_jack` stores mutex, ALSA jack, card, pin list, status, notifier chain, and voltage zones. APIs include `snd_soc_jack_report()`, pin/notifier/zone helpers, `snd_soc_jack_get_type()`, and GPIO add/free helpers with no-op stubs when GPIOLIB is disabled.

## Control flow
Machine or codec drivers create a jack, attach pins/zones/GPIOs, then call `snd_soc_jack_report()` from codec IRQs or GPIO work. Reporting updates jack status, toggles DAPM pins, and notifies listeners.

## State and persistence behavior
Jack state is runtime-only: current status, pin list, voltage zones, notifier subscribers, and GPIO work/resources. GPIO wake and debounce settings affect device runtime behavior but are not persisted.

## Dependencies and integration points
It integrates ALSA jack devices, ASoC cards/DAPM pins, GPIO descriptors, PM notifiers, delayed work, and codec-specific status callbacks.

## Risks and test signals
Risks include missing GPIO cleanup, inverted pin masks, debounce races, wake-source misconfiguration, GPIOLIB-disabled stubs masking unsupported hardware, and notifier ordering. Test signals include headset/headphone/mic detection, ADC zone classification, GPIO insert/remove with debounce, suspend wake, inverted pins, notifier register/unregister, and DAPM pin status changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-jack.h -->
