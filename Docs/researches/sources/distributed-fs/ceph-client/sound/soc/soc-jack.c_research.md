# sources/distributed-fs/ceph-client/sound/soc/soc-jack.c

## Purpose
This file implements ASoC jack status reporting and GPIO-backed jack detection. It connects ALSA jack devices, ASoC DAPM pin power, notifier callbacks, optional voltage zones, and GPIO interrupt/debounce handling into one jack abstraction used by machine and codec drivers.

## Important APIs, Types, and Functions
The main exported APIs are `snd_soc_jack_report()`, `snd_soc_jack_add_zones()`, `snd_soc_jack_get_type()`, `snd_soc_jack_add_pins()`, `snd_soc_jack_notifier_register()`, `snd_soc_jack_notifier_unregister()`, `snd_soc_jack_add_gpios()`, `snd_soc_jack_add_gpiods()`, and `snd_soc_jack_free_gpios()`. `struct snd_soc_jack` owns status, a mutex, DAPM pins, zones, and a blocking notifier chain. `struct snd_soc_jack_pin` maps jack bits to DAPM pins. `struct snd_soc_jack_gpio` stores GPIO descriptor, debounce work, IRQ behavior, wakeup policy, and optional custom status callback.

## Control Flow
`snd_soc_jack_report()` is the central update path. It masks in new status bits, updates each configured DAPM pin, notifies registered listeners before DAPM sync, synchronizes DAPM if pins changed, then calls `snd_jack_report()` for userspace. `snd_soc_jack_add_pins()` validates pin names and masks, registers ALSA jack controls for pins, and replays the last status through `snd_soc_jack_report()`.

With GPIOLIB enabled, `snd_soc_jack_add_gpios()` allocates devres cleanup state, resolves GPIO descriptors, initializes delayed work, requests shared rising/falling IRQs, optionally enables wake, registers a PM notifier, exports the GPIO for diagnostics, and schedules initial detection after debounce. IRQs only queue delayed work; `gpio_work()` reads the line with `gpiod_get_value_cansleep()`, applies inversion or `jack_status_check()`, and reports the result.

## State and Persistence
Jack state lives in `jack->status`, the pin and zone lists, registered notifier blocks, delayed work items, IRQ registrations, and devres cleanup records. GPIO cleanup unregisters PM notifiers, frees IRQs, cancels delayed work synchronously, unexports GPIOs, drops descriptors, and clears the back pointer.

## Dependencies and Integration Points
The file integrates ALSA jack core (`snd_jack_report`, `snd_jack_add_new_kctl`), ASoC DAPM (`snd_soc_dapm_enable_pin`, `disable_pin`, `sync`), GPIO descriptors, IRQs, PM notifiers, workqueues, wakeup events, and tracepoints. Voltage-zone helpers let codec-specific ADC/micbias detection translate millivolt ranges into jack types.

## Risks and Test Signals
Important risks are calling `snd_soc_jack_report()` from atomic context despite its mutex and DAPM operations, missing debounce after resume, stale work during GPIO teardown, misuse of `devres_destroy()` when manually freeing, and notifier callbacks attempting recursive reporting. Test signals include GPIO insertion/removal IRQ tests, suspend/resume transition detection, inverted GPIO behavior, DAPM pin enablement, voltage-zone matching at boundaries, and devres/manual cleanup leak checks.
