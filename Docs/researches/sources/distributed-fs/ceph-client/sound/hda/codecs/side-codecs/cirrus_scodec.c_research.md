# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.c

## Purpose
`cirrus_scodec.c` is a small shared library for Cirrus HD-audio side codecs. It currently provides speaker-ID GPIO decoding used to select tuning or calibration variants for multi-amp systems.

## APIs, Types, and Functions
The exported API is `cirrus_scodec_get_speaker_id(struct device *dev, int amp_index, int num_amps, int fixed_gpio_id)`, exported in namespace `SND_HDA_CIRRUS_SCODEC`. It uses GPIO descriptor APIs: `gpiod_get_index()`, `gpiod_count()`, `gpiod_get_value_cansleep()`, and `gpiod_put()`.

## Control Flow
If `fixed_gpio_id >= 0`, the function reads one unnamed GPIO index and returns that value. Otherwise it counts `spk-id-gpios`, divides them evenly across `num_amps`, computes the current amp's base index, validates divisibility, then reads each GPIO bit for that amp and assembles the speaker ID as a little-endian bitfield. If no GPIOs are present it returns `-ENOENT`.

## State and Persistence Behavior
The function is stateless. GPIO descriptors are acquired, read, and released during each call. The only persistence is external firmware/device-tree/ACPI property state that defines GPIO descriptors.

## Dependencies and Integration Points
Dependencies are Linux device logging, GPIO consumer APIs, module infrastructure, and `cirrus_scodec.h`. It integrates with side-codec drivers that need speaker IDs for firmware file naming or hardware configuration.

## Risks
The function assumes `gpiod_count()` is divisible by `num_amps`; malformed firmware returns `-EINVAL`. Bit ordering is implicit and must match board design. A failing GPIO read aborts with the first error and may prevent firmware selection.

## Test Signals
KUnit coverage in `cirrus_scodec_test.c`, fixed-GPIO and named-array paths, no-GPIO `-ENOENT`, invalid divisibility `-EINVAL`, multiple amps with shared/non-shared GPIO sets, and correct descriptor release are the main signals.
