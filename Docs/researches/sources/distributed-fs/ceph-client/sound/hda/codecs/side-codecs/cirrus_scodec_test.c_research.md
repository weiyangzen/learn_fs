# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec_test.c

## Purpose
`cirrus_scodec_test.c` is a KUnit suite for the Cirrus side-codec speaker-ID helper. It builds faux GPIO and amplifier devices, attaches software-node GPIO references, and verifies speaker-ID parsing over many amp/GPIO sharing layouts.

## APIs, Types, and Functions
Test state is held in `struct cirrus_scodec_test_gpio` and `struct cirrus_scodec_test_priv`. GPIO shim callbacks implement input-only behavior: get direction, direction input, get value, reject output/set operations, and accept non-output pin configs. Helpers include `cirrus_scodec_test_create_gpio()`, `cirrus_scodec_test_set_gpio_ref_arg()`, `cirrus_scodec_test_set_spkid_swnode()`, `cirrus_scodec_test_spkid_parse()`, `cirrus_scodec_test_no_spkid()`, and `cirrus_scodec_test_case_init()`.

## Control Flow
Each test creates a faux GPIO device and faux amp device. Parameterized cases build `spk-id-gpios` references for `num_amps * gpios_per_amp`, optionally reusing GPIO indices for shared groups. For every amp and every possible bit pattern, the test sets fake GPIO pin state and asserts that `cirrus_scodec_get_speaker_id()` returns the expected value. A separate case confirms that a device without speaker-ID GPIOs returns `-ENOENT`.

## State and Persistence Behavior
State is per-test KUnit allocation and faux-device devres. Cleanup actions destroy faux devices and remove software nodes. GPIO pin state is an in-memory bitmask on the fake gpiochip.

## Dependencies and Integration Points
Dependencies include KUnit resources, faux devices, software nodes, GPIO driver APIs, pinconf helpers, and `cirrus_scodec.h`. The module imports namespace `SND_HDA_CIRRUS_SCODEC`.

## Risks
The test focuses on named `spk-id-gpios`; it does not cover the fixed unnamed GPIO path or malformed counts returning `-EINVAL`. Shared-GPIO logic is subtle and could miss invalid firmware layouts outside the parameter matrix.

## Test Signals
Passing `snd-hda-cirrus-scodec-test`, all parameter descriptions, all amp counts from two to four, one to four GPIOs per amp, all-shared and pair-shared cases, and the no-GPIO negative case are primary signals.
